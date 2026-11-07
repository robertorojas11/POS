import json
import unittest
from decimal import Decimal
from app import create_app, db
from app.models.user import User, UserType
from app.models.product import Product
from app.models.sale import Sale, Discount


class CheckoutTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()
        db.drop_all()
        db.create_all()
        for ut_id, name in [(1, "Admin"), (2, "Manager"), (3, "Operator")]:
            db.session.add(UserType(id=ut_id, name=name))
        self._user("op", 3)
        self._user("mgr", 2)
        self.product = Product(sku="A", name="Cola", price=Decimal("2.00"), cost_price=Decimal("1"),
                               stock_quantity=10, min_sale_qty=1)
        self.kilo = Product(sku="K", name="Tomato", price=Decimal("4.00"), cost_price=Decimal("1"),
                            stock_quantity=10, min_sale_qty=Decimal("0.25"), uom="kilograms")
        db.session.add_all([self.product, self.kilo, Discount(code="TEN", discount_type="percent", value=10)])
        db.session.commit()
        self.op_h = self._login("op")
        self.mgr_h = self._login("mgr")
        for h in (self.op_h, self.mgr_h):
            self.client.post('/api/sales/shifts/start', headers=h, json={"start_cash": 0})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _user(self, name, type_id):
        u = User(username=name, email=f"{name}@x.com", user_type_id=type_id)
        u.set_password("password123")
        db.session.add(u)

    def _login(self, name):
        r = self.client.post('/api/auth/login', json={"username": name, "password": "password123"})
        return {'Authorization': f'Bearer {r.get_json()["access_token"]}'}

    def _checkout(self, body, headers=None):
        return self.client.post('/api/sales/checkout', headers=headers or self.op_h, json=body)

    def _item(self, qty, product=None):
        return {"product_id": (product or self.product).id, "quantity": qty}

    def _stock(self, product):
        db.session.expire_all()
        return float(db.session.get(Product, product.id).stock_quantity)

    def test_totals_use_server_tax_and_rounding(self):
        r = self._checkout({"items": [self._item(2)], "payment_method": "cash", "tax_rate": 0})
        self.assertEqual(r.status_code, 201)
        sale = r.get_json()["sale"]
        self.assertEqual((sale["subtotal"], sale["tax"], sale["total"]), (4.00, 0.33, 4.33))  # client tax_rate ignored
        self.assertEqual(self._stock(self.product), 8)

    def test_rejects_bad_quantities(self):
        for qty in (-1, 0, "abc", 0.5):  # 0.5 is not a multiple of min_sale_qty=1
            r = self._checkout({"items": [self._item(qty)], "payment_method": "cash"})
            self.assertEqual(r.status_code, 400, qty)
        self.assertEqual(self._stock(self.product), 10)

    def test_fractional_step_enforced(self):
        self.assertEqual(self._checkout({"items": [self._item(1.5, self.kilo)], "payment_method": "cash"}).status_code, 201)
        self.assertEqual(self._checkout({"items": [self._item(0.3, self.kilo)], "payment_method": "cash"}).status_code, 400)

    def test_duplicate_lines_are_merged_for_stock_check(self):
        r = self._checkout({"items": [self._item(6), self._item(6)], "payment_method": "cash"})
        self.assertEqual(r.status_code, 400)  # 12 > 10; checked per line it would have passed twice

    def test_insufficient_stock_rolls_back(self):
        r = self._checkout({"items": [self._item(1), self._item(11, self.kilo)], "payment_method": "cash"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self._stock(self.product), 10)
        self.assertEqual(Sale.query.count(), 0)

    def test_manual_discount_needs_manager_and_is_capped(self):
        body = {"items": [self._item(1)], "payment_method": "cash", "discount": 1}
        self.assertEqual(self._checkout(body).status_code, 400)
        huge = self._checkout({**body, "discount": 1000000}, self.mgr_h).get_json()["sale"]
        self.assertEqual((huge["discount"], huge["total"]), (2.00, 0.00))  # capped at subtotal

    def test_discount_code_computed_by_server(self):
        r = self._checkout({"items": [self._item(5)], "payment_method": "cash", "discount_code": "ten", "discount": 999})
        self.assertEqual(r.get_json()["sale"]["discount"], 1.00)
        bad = self._checkout({"items": [self._item(1)], "payment_method": "cash", "discount_code": "NOPE"})
        self.assertEqual(bad.status_code, 400)

    def test_split_must_add_up(self):
        base = {"items": [self._item(2)], "payment_method": "split"}  # total 4.33
        bad = self._checkout({**base, "payment_details": {"cash": 1, "card": 1}})
        self.assertEqual(bad.status_code, 400)
        ok = self._checkout({**base, "payment_details": {"cash": 1.33, "card": 3}})
        self.assertEqual(ok.status_code, 201)

    def test_unknown_payment_method(self):
        self.assertEqual(self._checkout({"items": [self._item(1)], "payment_method": "bitcoin"}).status_code, 400)

    def test_client_ref_makes_checkout_idempotent(self):
        body = {"items": [self._item(2)], "payment_method": "cash", "client_ref": "till-1-abc"}
        first = self._checkout(body).get_json()["sale"]
        second = self._checkout(body).get_json()["sale"]
        self.assertEqual(first["invoice_number"], second["invoice_number"])
        self.assertEqual(Sale.query.count(), 1)
        self.assertEqual(self._stock(self.product), 8)  # charged once

    def test_second_open_shift_refused(self):
        r = self.client.post('/api/sales/shifts/start', headers=self.op_h, json={"start_cash": 0})
        self.assertEqual(r.status_code, 400)

    def test_config_endpoint_is_public_and_has_no_secrets(self):
        data = self.client.get('/api/config').get_json()
        self.assertEqual(data["business_type"], "retail")
        self.assertEqual(data["tax_rate"], 0.0825)
        self.assertNotIn("secret", json.dumps(data).lower())


if __name__ == '__main__':
    unittest.main()
