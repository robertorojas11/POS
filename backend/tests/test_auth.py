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
        db.session.execute(db.delete(User))
        db.session.execute(db.delete(UserType))
        db.session.commit()
        
        # Seed user types for tests
        for ut_id, ut_name in [(1, "Admin"), (2, "Manager"), (3, "Operator")]:
            if not db.session.get(UserType, ut_id):
                db.session.add(UserType(id=ut_id, name=ut_name))
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

    def test_employee_crud_and_auditing(self):
        from app.models.store import Store

        # 1. Register and login as Admin
        admin = User(username="admin_user", email="admin@example.com", user_type_id=1)
        admin.set_password("adminpass")
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id

        payload = {"username": "admin_user", "password": "adminpass"}
        response = self.client.post('/api/auth/login', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        login_data = json.loads(response.data.decode('utf-8'))
        headers = {'Authorization': f'Bearer {login_data["access_token"]}'}

        # 2. Create a Store and verify created_by_id
        store_payload = {
            "name": "East Sucursal",
            "code": "EST",
            "location": "First Floor",
            "address": "123 East Rd"
        }
        response = self.client.post('/api/stores', data=json.dumps(store_payload), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 201)
        store_data = json.loads(response.data.decode('utf-8'))
        store_id = store_data['id']
        self.assertEqual(store_data['created_by_id'], admin_id)

        # 3. Create an Employee and verify created_by_id
        emp_payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "contact_phone": "1234567890",
            "user_type_id": 3,
            "store_id": store_id
        }
        response = self.client.post('/api/auth/employees', data=json.dumps(emp_payload), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 201)
        emp_data = json.loads(response.data.decode('utf-8'))
        emp_id = emp_data['user']['id']
        self.assertEqual(emp_data['user']['created_by_id'], admin_id)
        self.assertEqual(emp_data['user']['store_id'], store_id)

        # 4. Update the Employee and verify updated_by_id
        update_payload = {
            "first_name": "Jane Modified",
            "contact_phone": "9876543210"
        }
        response = self.client.put(f'/api/auth/employees/{emp_id}', data=json.dumps(update_payload), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        updated_emp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(updated_emp['first_name'], "Jane Modified")
        self.assertEqual(updated_emp['updated_by_id'], admin_id)

        # 5. Update the Store and verify updated_by_id
        update_store_payload = {
            "name": "East Sucursal Modified",
            "location": "Second Floor"
        }
        response = self.client.put(f'/api/stores/{store_id}', data=json.dumps(update_store_payload), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        updated_store = json.loads(response.data.decode('utf-8'))
        self.assertEqual(updated_store['name'], "East Sucursal Modified")
        self.assertEqual(updated_store['updated_by_id'], admin_id)

        # 6. Delete the Employee
        response = self.client.delete(f'/api/auth/employees/{emp_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        # Verify deletion
        emp_check = db.session.get(User, emp_id)
        self.assertIsNone(emp_check)

if __name__ == '__main__':
    unittest.main()
