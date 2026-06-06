import unittest
import json
from datetime import datetime
from app import create_app, db
from app.models.user import User, UserType
from app.models.product import Category, Product
from app.models.shift import Shift
from app.models.sale import Sale, Discount

class ShiftTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        db.session.execute(db.delete(Discount))
        db.session.execute(db.delete(Sale))
        db.session.execute(db.delete(Shift))
        db.session.execute(db.delete(Product))
        db.session.execute(db.delete(Category))
        db.session.execute(db.delete(User))
        db.session.execute(db.delete(UserType))
        db.session.commit()
        
        # Seed user types
        for ut_id, ut_name in [(1, "Admin"), (2, "Manager"), (3, "Operator")]:
            if not db.session.get(UserType, ut_id):
                db.session.add(UserType(id=ut_id, name=ut_name))
        db.session.commit()
        
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

    def test_active_shifts_all(self):
        # 1. Create an admin user and login
        admin_user = User(username="admin1", email="admin1@example.com", user_type_id=1)
        admin_user.set_password("adminpass")
        db.session.add(admin_user)
        db.session.commit()
        
        admin_login = self.client.post('/api/auth/login', data=json.dumps({"username": "admin1", "password": "adminpass"}), content_type='application/json')
        admin_data = json.loads(admin_login.data.decode('utf-8'))
        admin_headers = {'Authorization': f'Bearer {admin_data["access_token"]}'}
        
        # 2. Check active-all with no open shifts
        res = self.client.get('/api/sales/shifts/active-all', headers=admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(json.loads(res.data.decode('utf-8'))), 0)
        
        # 3. Start a shift with cashier
        start_payload = {"start_cash": 150.00}
        self.client.post(
            '/api/sales/shifts/start',
            headers=self.headers,
            data=json.dumps(start_payload),
            content_type='application/json'
        )
        
        # 4. Check active-all again
        res = self.client.get('/api/sales/shifts/active-all', headers=admin_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["start_cash"], 150.00)
        self.assertEqual(data[0]["cashier_name"], "cashier1")
        self.assertEqual(data[0]["expected_cash"], 150.00)
        
        # 5. Accessing active-all as Operator should be forbidden (403)
        res_op = self.client.get('/api/sales/shifts/active-all', headers=self.headers)
        self.assertEqual(res_op.status_code, 403)

    def test_discount_validation(self):
        # 1. Create a discount code
        discount = Discount(code="SAVE10", discount_type="percent", value=10.00, is_active=True)
        db.session.add(discount)
        db.session.commit()
        
        # 2. Validate valid discount code
        res = self.client.get('/api/sales/discounts/validate/SAVE10', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(data["code"], "SAVE10")
        self.assertEqual(data["discount_type"], "percent")
        self.assertEqual(data["value"], 10.00)
        
        # 3. Validate case insensitivity and whitespace handling
        res2 = self.client.get('/api/sales/discounts/validate/ save10 ', headers=self.headers)
        self.assertEqual(res2.status_code, 200)
        
        # 4. Validate inactive discount code
        discount.is_active = False
        db.session.commit()
        res3 = self.client.get('/api/sales/discounts/validate/SAVE10', headers=self.headers)
        self.assertEqual(res3.status_code, 404)
        
        # 5. Validate non-existent code
        res4 = self.client.get('/api/sales/discounts/validate/NOTREAL', headers=self.headers)
        self.assertEqual(res4.status_code, 404)

    def test_product_uom(self):
        # 1. Login as Admin/Manager to create product
        admin_user = User(username="admin_prod", email="admin_prod@example.com", user_type_id=1)
        admin_user.set_password("adminpass")
        db.session.add(admin_user)
        db.session.commit()
        
        admin_login = self.client.post('/api/auth/login', data=json.dumps({"username": "admin_prod", "password": "adminpass"}), content_type='application/json')
        admin_headers = {'Authorization': f'Bearer {json.loads(admin_login.data.decode("utf-8"))["access_token"]}'}
        
        # 2. Create product with kilograms UOM
        payload = {
            "sku": "PROD-KG",
            "name": "Organic Tomatoes",
            "price": 3.99,
            "cost_price": 1.50,
            "stock_quantity": 25.500,
            "min_stock_level": 2.000,
            "uom": "kilograms"
        }
        res = self.client.post(
            '/api/products',
            headers=admin_headers,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(data["uom"], "kilograms")
        self.assertEqual(data["stock_quantity"], 25.5)
        
        # 3. Update product UOM to pounds
        update_payload = {"uom": "pounds"}
        res_update = self.client.put(
            f'/api/products/{data["id"]}',
            headers=admin_headers,
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(res_update.status_code, 200)
        data_update = json.loads(res_update.data.decode('utf-8'))
        self.assertEqual(data_update["uom"], "pounds")

    def test_product_events_stream(self):
        # 1. Access SSE stream
        res = self.client.get('/api/products/events')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, 'text/event-stream')
        data = res.get_data(as_text=True)
        self.assertIn("connected", data)

    def test_terminal_specific_cache_routing(self):
        # Fetching products with terminal-specific headers should succeed
        res_t1 = self.client.get('/api/products', headers={'X-Terminal-Id': 'terminal_A', 'Authorization': self.headers['Authorization']})
        self.assertEqual(res_t1.status_code, 200)
        
        res_t2 = self.client.get('/api/products', headers={'X-Terminal-Id': 'terminal_B', 'Authorization': self.headers['Authorization']})
        self.assertEqual(res_t2.status_code, 200)




