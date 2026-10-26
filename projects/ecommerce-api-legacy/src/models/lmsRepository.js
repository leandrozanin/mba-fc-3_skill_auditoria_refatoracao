const crypto = require('node:crypto');
const sqlite3 = require('sqlite3').verbose();

class LmsRepository {
    constructor(database = ':memory:') {
        this.db = new sqlite3.Database(database);
    }

    run(sql, parameters = []) {
        return new Promise((resolve, reject) => {
            this.db.run(sql, parameters, function onRun(error) {
                if (error) return reject(error);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    get(sql, parameters = []) {
        return new Promise((resolve, reject) => {
            this.db.get(sql, parameters, (error, row) => {
                if (error) return reject(error);
                resolve(row);
            });
        });
    }

    all(sql, parameters = []) {
        return new Promise((resolve, reject) => {
            this.db.all(sql, parameters, (error, rows) => {
                if (error) return reject(error);
                resolve(rows);
            });
        });
    }

    async initialize() {
        await this.run('PRAGMA foreign_keys = ON');
        await this.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, pass TEXT NOT NULL)');
        await this.run('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL CHECK(price >= 0), active INTEGER NOT NULL DEFAULT 1)');
        await this.run('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, course_id INTEGER NOT NULL REFERENCES courses(id), UNIQUE(user_id, course_id))');
        await this.run('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE, amount REAL NOT NULL, status TEXT NOT NULL)');
        await this.run('CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT NOT NULL, created_at DATETIME NOT NULL)');
        const row = await this.get('SELECT COUNT(*) AS total FROM courses');
        if (row.total === 0) {
            await this.run('INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)', [
                'Clean Architecture', 997, 1, 'Docker', 497, 1,
            ]);
        }
    }

    async createCheckout({ name, email, password, courseId, card }) {
        await this.run('BEGIN IMMEDIATE');
        try {
            const course = await this.get('SELECT id, title, price FROM courses WHERE id = ? AND active = 1', [courseId]);
            if (!course) {
                const error = new Error('Curso não encontrado');
                error.statusCode = 404;
                throw error;
            }
            let user = await this.get('SELECT id FROM users WHERE email = ?', [email]);
            if (!user) {
                const salt = crypto.randomBytes(16);
                const passwordHash = crypto.scryptSync(password, salt, 64).toString('hex');
                const result = await this.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
                    name, email, `${salt.toString('hex')}:${passwordHash}`,
                ]);
                user = { id: result.lastID };
            }
            const existing = await this.get('SELECT id FROM enrollments WHERE user_id = ? AND course_id = ?', [user.id, courseId]);
            if (existing) {
                const error = new Error('Usuário já matriculado no curso');
                error.statusCode = 409;
                throw error;
            }
            const enrollment = await this.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [user.id, courseId]);
            await this.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollment.lastID, course.price, 'PAID']);
            await this.run('INSERT INTO audit_logs (action, created_at) VALUES (?, datetime(\'now\'))', [`Checkout curso ${courseId} por ${user.id}`]);
            await this.run('COMMIT');
            return { enrollmentId: enrollment.lastID };
        } catch (error) {
            await this.run('ROLLBACK').catch(() => {});
            throw error;
        }
    }

    async getFinancialReport() {
        const rows = await this.all(
            `SELECT c.id AS course_id, c.title, e.id AS enrollment_id, u.name AS student_name,
                    p.amount, p.status
             FROM courses c
             LEFT JOIN enrollments e ON e.course_id = c.id
             LEFT JOIN users u ON u.id = e.user_id
             LEFT JOIN payments p ON p.enrollment_id = e.id
             ORDER BY c.id, e.id`
        );
        const courses = new Map();
        for (const row of rows) {
            const course = courses.get(row.course_id) || { course: row.title, revenue: 0, students: [] };
            if (row.enrollment_id !== null) {
                const paid = row.amount || 0;
                if (row.status === 'PAID') course.revenue += paid;
                course.students.push({ student: row.student_name || 'Unknown', paid });
            }
            courses.set(row.course_id, course);
        }
        return [...courses.values()];
    }

    async deleteUser(userId) {
        await this.run('BEGIN IMMEDIATE');
        try {
            const user = await this.get('SELECT id FROM users WHERE id = ?', [userId]);
            if (!user) {
                await this.run('ROLLBACK');
                return false;
            }
            await this.run(
                'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)',
                [userId],
            );
            await this.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
            await this.run('DELETE FROM users WHERE id = ?', [userId]);
            await this.run('COMMIT');
            return true;
        } catch (error) {
            await this.run('ROLLBACK').catch(() => {});
            throw error;
        }
    }

    close() {
        return new Promise((resolve, reject) => {
            this.db.close((error) => error ? reject(error) : resolve());
        });
    }
}

module.exports = LmsRepository;
