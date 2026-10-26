from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db


def _serialize(row):
    if not row:
        return None
    return {key: row[key] for key in ("id", "nome", "email", "tipo", "criado_em")}


def list_users():
    rows = get_db().execute("SELECT * FROM usuarios ORDER BY id").fetchall()
    return [_serialize(row) for row in rows]


def get_user(user_id):
    row = get_db().execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
    return _serialize(row)


def create_user(name, email, password, role="cliente"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (name, email, generate_password_hash(password), role),
    )
    db.commit()
    return cursor.lastrowid


def authenticate(email, password):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if not row:
        return None
    stored_password = row["senha"] or ""
    if stored_password.startswith(("scrypt:", "pbkdf2:")):
        valid = check_password_hash(stored_password, password)
    else:
        valid = stored_password == password
        if valid:
            db.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (generate_password_hash(password), row["id"]))
            db.commit()
    return _serialize(row) if valid else None


def email_exists(email):
    return get_db().execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone() is not None
