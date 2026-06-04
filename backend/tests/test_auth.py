import unittest
import json
from app import create_app, db
from app.models.user import User, UserType

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Seed user types for tests
        admin_type = UserType(id=1, name="Admin")
        manager_type = UserType(id=2, name="Manager")
        operator_type = UserType(id=3, name="Operator")
        db.session.add_all([admin_type, manager_type, operator_type])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration(self):
        payload = {
            "username": "cashier1",
            "email": "cashier1@example.com",
            "password": "securepassword",
            "role": "cashier"
        }
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['user']['username'], 'cashier1')
        self.assertEqual(data['user']['role'], 'operator') # cashier maps to operator
        self.assertEqual(data['user']['user_type_id'], 3)

    def test_user_login(self):
        # Register a user first
        user = User(username="admin", email="admin@example.com", user_type_id=1)
        user.set_password("adminpass")
        db.session.add(user)
        db.session.commit()
        
        # Try to login
        payload = {
            "username": "admin",
            "password": "adminpass"
        }
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('access_token', data)
        self.assertEqual(data['user']['role'], 'admin')

if __name__ == '__main__':
    unittest.main()
