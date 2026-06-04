import unittest
import json
from datetime import datetime
from app import create_app, db
from app.models.user import User, UserType
from app.models.product import Category, Product
from app.models.shift import Shift
from app.models.sale import Sale

class ShiftTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Seed user types
        admin_type = UserType(id=1, name="Admin")
        manager_type = UserType(id=2, name="Manager")
        operator_type = UserType(id=3, name="Operator")
        db.session.add_all([admin_type, manager_type, operator_type])
        
        # Create cashier user
        self.cashier = User(username="cashier1", email="cashier1@example.com", user_type_id=3)
        self.cashier.set_password("securepassword")
        db.session.add(self.cashier)
        
        # Create a product for checkout tests
        self.category = Category(name="Drinks")
        db.session.add(self.category)
        db.session.flush()
        
        self.product = Product(
            sku="BEV-COLA",
            barcode="123456",
            name="Classic Cola",
            price=2.00,
            cost_price=0.80,
            stock_quantity=10,
            category_id=self.category.id
        )
        db.session.add(self.product)
        db.session.commit()
        
        # Authenticate cashier and save headers
        payload = {"username": "cashier1", "password": "securepassword"}
        response = self.client.post('/api/auth/login', data=json.dumps(payload), content_type='application/json')
        data = json.loads(response.data.decode('utf-8'))
        self.headers = {'Authorization': f'Bearer {data["access_token"]}'}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_checkout_fails_without_active_shift(self):
        payload = {
            "items": [{"product_id": self.product.id, "quantity": 2}],
            "payment_method": "cash"
        }
        response = self.client.post(
            '/api/sales/checkout',
            headers=self.headers,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn("No open cash shift found", data["error"])

    def test_start_and_close_shift(self):
        # 1. Start shift with 100.00 cash
        start_payload = {"start_cash": 100.00}
        response = self.client.post(
            '/api/sales/shifts/start',
            headers=self.headers,
            data=json.dumps(start_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data["status"], "open")
        self.assertEqual(data["start_cash"], 100.00)
        
        # 2. Complete checkout with cash (2 colas = 4.00)
        checkout_payload = {
            "items": [{"product_id": self.product.id, "quantity": 2}],
            "payment_method": "cash"
        }
        checkout_res = self.client.post(
            '/api/sales/checkout',
            headers=self.headers,
            data=json.dumps(checkout_payload),
            content_type='application/json'
        )
        self.assertEqual(checkout_res.status_code, 201)
        
        # 3. Check active shift details (expected cash should be 104.33: 100.00 start + 4.33 sale including tax)
        active_res = self.client.get('/api/sales/shifts/active', headers=self.headers)
        self.assertEqual(active_res.status_code, 200)
        active_data = json.loads(active_res.data.decode('utf-8'))
        self.assertTrue(active_data["active"])
        self.assertEqual(active_data["shift"]["expected_cash"], 104.33)
        
        # 4. Close shift with 105.00 cash in drawer (actual cash), expecting 0.67 surplus variance
        close_payload = {"actual_cash": 105.00}
        close_res = self.client.post(
            '/api/sales/shifts/close',
            headers=self.headers,
            data=json.dumps(close_payload),
            content_type='application/json'
        )
        self.assertEqual(close_res.status_code, 200)
        close_data = json.loads(close_res.data.decode('utf-8'))
        report = close_data["report"]
        self.assertEqual(report["status"], "closed")
        self.assertEqual(report["expected_cash"], 104.33)
        self.assertEqual(report["actual_cash"], 105.00)
        self.assertEqual(report["variance"], 0.67)
