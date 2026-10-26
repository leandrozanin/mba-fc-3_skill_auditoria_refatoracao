import os
import tempfile
import unittest

from app import create_app, db
from models.user import User
from services.notification_service import NotificationService
from seed import seed_data


class TaskManagerApiTests(unittest.TestCase):
    def setUp(self):
        self.database = tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False)
        self.database.close()
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.database.name}', 'SECRET_KEY': 'test-secret'})
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()
        os.unlink(self.database.name)

    def test_health_does_not_expose_secrets_or_debug_data(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'ok')
        self.assertNotIn('secret', str(response.json).lower())
        self.assertNotIn('debug', response.json)

    def test_users_never_serialize_password_hash(self):
        response = self.client.post('/users', json={
            'name': 'Test User', 'email': 'test@example.com', 'password': 'strong-password'
        })
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.json)
        self.assertNotIn('password', self.client.get('/users').json[0])

    def test_password_uses_adaptive_hash_and_login_succeeds(self):
        response = self.client.post('/users', json={
            'name': 'Test User', 'email': 'test@example.com', 'password': 'strong-password'
        })
        with self.app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            self.assertTrue(user.password.startswith('scrypt:'))
        login = self.client.post('/login', json={'email': 'test@example.com', 'password': 'strong-password'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(login.status_code, 200)
        self.assertNotIn('password', login.json['user'])

    def test_task_creation_validates_non_numeric_priority(self):
        response = self.client.post('/tasks', json={'title': 'Valid title', 'priority': 'bad'})
        self.assertEqual(response.status_code, 400)

    def test_notification_service_does_not_embed_smtp_credentials(self):
        service = NotificationService()
        self.assertEqual(service.email_user, os.environ.get('SMTP_USER', ''))
        self.assertNotEqual(service.email_password, 'senha123')

    def test_seeded_read_routes_and_summary_report_remain_available(self):
        seed_data(self.app)
        paths = [
            '/', '/health', '/tasks', '/tasks/1', '/tasks/search', '/tasks/stats',
            '/users', '/users/1', '/users/1/tasks', '/reports/summary',
            '/reports/user/1', '/categories',
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)


if __name__ == '__main__':
    unittest.main()
