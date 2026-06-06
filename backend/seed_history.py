import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app, db
from app.models.user import User, UserType
from app.models.product import Category, Product
from app.models.customer import Customer
from app.models.shift import Shift
from app.models.sale import Sale, SaleItem, Discount
from app.models.inventory import InventoryLog
from app.models.store import Store

def seed_historical_database():
    app = create_app(os.getenv('FLASK_CONFIG', 'default'))
    with app.app_context():
        print("Cleaning old data for a fresh seed...")
        # Clear in reverse order of foreign keys to avoid constraints crashes
        db.session.query(InventoryLog).delete()
        db.session.query(SaleItem).delete()
        db.session.query(Sale).delete()
        db.session.query(Shift).delete()
        db.session.query(User).delete()
        db.session.query(UserType).delete()
        db.session.query(Product).delete()
        db.session.query(Category).delete()
        db.session.query(Customer).delete()
        db.session.query(Discount).delete()
        db.session.query(Store).delete()
        db.session.commit()

        print("Seeding user types...")
        admin_type = UserType(id=1, name="Admin")
        manager_type = UserType(id=2, name="Manager")
        operator_type = UserType(id=3, name="Operator")
        db.session.add_all([admin_type, manager_type, operator_type])
        db.session.flush()

        print("Seeding stores...")
        west_wing = Store(name="West Wing", code="W", location="Building A, Wing 1", address="100 Main St, West Wing")
        central_aisle = Store(name="Central Aisle", code="C", location="Building B, Central Corridor", address="100 Main St, Central Aisle")
        db.session.add_all([west_wing, central_aisle])
        db.session.flush()

        print("Seeding users (with employee profiles)...")
        admin = User(
            username="admin", email="admin@apexpos.com", user_type_id=admin_type.id,
            first_name="System", last_name="Administrator", second_last_name=None,
            contact_phone="555-0001", must_change_password=False, store_id=None
        )
        admin.set_password("admin")
        db.session.add(admin)

        manager1 = User(
            username="manager1", email="manager1@apexpos.com", user_type_id=manager_type.id,
            first_name="Sarah", last_name="Connor", second_last_name="Reese",
            contact_phone="555-1001", must_change_password=False, store_id=central_aisle.id
        )
        manager1.set_password("securepassword")
        db.session.add(manager1)

        manager2 = User(
            username="manager2", email="manager2@apexpos.com", user_type_id=manager_type.id,
            first_name="Bruce", last_name="Wayne", second_last_name="Thomas",
            contact_phone="555-1002", must_change_password=False, store_id=west_wing.id
        )
        manager2.set_password("securepassword")
        db.session.add(manager2)

        cashier1 = User(
            username="cashier1", email="cashier1@apexpos.com", user_type_id=operator_type.id,
            first_name="John", last_name="Doe", second_last_name="William",
            contact_phone="555-2001", must_change_password=False, store_id=west_wing.id
        )
        cashier1.set_password("securepassword")
        db.session.add(cashier1)

        cashier2 = User(
            username="cashier2", email="cashier2@apexpos.com", user_type_id=operator_type.id,
            first_name="Jane", last_name="Smith", second_last_name="Marie",
            contact_phone="555-2002", must_change_password=False, store_id=west_wing.id
        )
        cashier2.set_password("securepassword")
        db.session.add(cashier2)

        cashier3 = User(
            username="cashier3", email="cashier3@apexpos.com", user_type_id=operator_type.id,
            first_name="Peter", last_name="Parker", second_last_name="Benjamin",
            contact_phone="555-2003", must_change_password=False, store_id=central_aisle.id
        )
        cashier3.set_password("securepassword")
        db.session.add(cashier3)

        cashier4 = User(
            username="cashier4", email="cashier4@apexpos.com", user_type_id=operator_type.id,
            first_name="Diana", last_name="Prince", second_last_name="Diana",
            contact_phone="555-2004", must_change_password=False, store_id=central_aisle.id
        )
        cashier4.set_password("securepassword")
        db.session.add(cashier4)

        db.session.flush()

        print("Seeding product categories...")
        beverages = Category(name="Beverages", description="Soft drinks, coffee, tea, and juice")
        snacks = Category(name="Snacks", description="Chips, candy, pretzels, and cookies")
        produce = Category(name="Produce", description="Fresh fruits and vegetables sold by weight")
        electronics = Category(name="Electronics", description="Cables, adapters, chargers, and small accessories")
        bakery = Category(name="Bakery", description="Fresh bread, buns, cookies, and pastries")
        apparel = Category(name="Apparel", description="ApexPOS branded shirts, caps, and merchandise")
        
        db.session.add_all([beverages, snacks, produce, electronics, bakery, apparel])
        db.session.flush()

        print("Seeding products...")
        cola = Product(sku="BEV-COLA-01", barcode="012000000133", name="Classic Cola 12oz", description="Refreshing carbonated cola", price=1.99, cost_price=0.60, stock_quantity=150.0, min_stock_level=20.0, category_id=beverages.id, uom="pieces", min_sale_qty=1.0)
        milk = Product(sku="BEV-MILK-01", barcode="041000012938", name="Organic Whole Milk 1L", description="Fresh organic whole milk carton", price=2.99, cost_price=1.20, stock_quantity=60.0, min_stock_level=10.0, category_id=beverages.id, uom="liters", min_sale_qty=1.0)
        chips = Product(sku="SNK-CHIP-01", barcode="028400091496", name="Sea Salt Potato Chips", description="Crispy salted potato chips bag", price=2.49, cost_price=1.00, stock_quantity=110.0, min_stock_level=15.0, category_id=snacks.id, uom="pieces", min_sale_qty=1.0)
        apples = Product(sku="PRD-APPL-01", barcode="0000000094011", name="Organic Honeycrisp Apples", description="Crisp sweet organic apples", price=3.00, cost_price=1.10, stock_quantity=180.500, min_stock_level=25.0, category_id=produce.id, uom="kilograms", min_sale_qty=0.25)
        bananas = Product(sku="PRD-BANA-01", barcode="0000000094012", name="Sweet Cavendish Bananas", description="Fresh sweet yellow bananas", price=1.80, cost_price=0.60, stock_quantity=220.350, min_stock_level=30.0, category_id=produce.id, uom="kilograms", min_sale_qty=0.25)
        cable = Product(sku="ELC-USBC-01", barcode="884838291044", name="Braided USB-C Cable 6ft", description="High-speed charging USB type C cable", price=9.99, cost_price=3.50, stock_quantity=4.0, min_stock_level=5.0, category_id=electronics.id, uom="pieces", min_sale_qty=1.0)
        bread = Product(sku="BAK-BRED-01", barcode="072938102938", name="Whole Wheat Bread", description="Freshly baked organic whole wheat loaf", price=3.49, cost_price=1.50, stock_quantity=35.0, min_stock_level=8.0, category_id=bakery.id, uom="pieces", min_sale_qty=1.0)
        cookie = Product(sku="BAK-COOK-02", barcode="034000002451", name="Chocolate Chip Cookie", description="Soft-baked cookie with milk chocolate chips", price=1.25, cost_price=0.40, stock_quantity=85.0, min_stock_level=15.0, category_id=bakery.id, uom="pieces", min_sale_qty=1.0)
        tshirt = Product(sku="APP-TSHR-01", barcode="729381029381", name="ApexPOS Logo T-Shirt", description="100% cotton branded graphic tee shirt", price=19.99, cost_price=8.00, stock_quantity=25.0, min_stock_level=5.0, category_id=apparel.id, uom="pieces", min_sale_qty=1.0)
        
        db.session.add_all([cola, milk, chips, apples, bananas, cable, bread, cookie, tshirt])
        db.session.flush()

        print("Seeding customers...")
        john = Customer(name="John Doe", phone="555-0199", email="john.doe@example.com", loyalty_points=150)
        alice = Customer(name="Alice Smith", phone="555-0212", email="alice.smith@example.com", loyalty_points=45)
        bob = Customer(name="Bob Miller", phone="555-0344", email="bob.miller@example.com", loyalty_points=280)
        david = Customer(name="David Green", phone="555-0455", email="david.green@example.com", loyalty_points=10)
        emily = Customer(name="Emily Davis", phone="555-0566", email="emily.davis@example.com", loyalty_points=95)
        michael = Customer(name="Michael Brown", phone="555-0677", email="michael.brown@example.com", loyalty_points=60)
        db.session.add_all([john, alice, bob, david, emily, michael])
        db.session.flush()

        print("Seeding promotional discount codes...")
        spring_promo = Discount(code="SPRING20", discount_type="percent", value=20.00, is_active=True)
        summer_promo = Discount(code="SUMMER10", discount_type="percent", value=10.00, is_active=True)
        welcome_promo = Discount(code="WELCOME5", discount_type="fixed", value=5.00, is_active=True)
        winter_promo = Discount(code="WINTER15", discount_type="percent", value=15.00, is_active=True)
        emp_promo = Discount(code="EMP10", discount_type="percent", value=10.00, is_active=True)
        db.session.add_all([spring_promo, summer_promo, welcome_promo, winter_promo, emp_promo])
        db.session.flush()

        # Define custom timestamps for the past 5 days
        now = datetime.utcnow()
        days_ago_5 = now - timedelta(days=5)
        days_ago_4 = now - timedelta(days=4)
        days_ago_3 = now - timedelta(days=3)
        days_ago_2 = now - timedelta(days=2)
        days_ago_1 = now - timedelta(days=1)

        print("Generating historical shifts...")
        # Day 5 shifts
        shift_d5_morn = Shift(id=str(uuid.uuid4()), cashier_id=cashier1.id, start_time=days_ago_5 + timedelta(hours=8), end_time=days_ago_5 + timedelta(hours=16), start_cash=150.00, status="closed", terminal_id="terminal_01", store_location="West Wing", created_by_id=cashier1.id)
        shift_d5_eve = Shift(id=str(uuid.uuid4()), cashier_id=cashier2.id, start_time=days_ago_5 + timedelta(hours=16), end_time=days_ago_5 + timedelta(hours=22), start_cash=150.00, status="closed", terminal_id="terminal_01", store_location="West Wing", created_by_id=cashier2.id)

        # Day 4 shifts
        shift_d4_morn = Shift(id=str(uuid.uuid4()), cashier_id=manager1.id, start_time=days_ago_4 + timedelta(hours=9), end_time=days_ago_4 + timedelta(hours=17), start_cash=200.00, status="closed", terminal_id="terminal_02", store_location="Central Aisle", created_by_id=manager1.id)
        shift_d4_eve = Shift(id=str(uuid.uuid4()), cashier_id=cashier3.id, start_time=days_ago_4 + timedelta(hours=17), end_time=days_ago_4 + timedelta(hours=23), start_cash=150.00, status="closed", terminal_id="terminal_02", store_location="Central Aisle", created_by_id=cashier3.id)

        # Day 3 shifts
        shift_d3_morn = Shift(id=str(uuid.uuid4()), cashier_id=cashier1.id, start_time=days_ago_3 + timedelta(hours=8), end_time=days_ago_3 + timedelta(hours=16), start_cash=150.00, status="closed", terminal_id="terminal_01", store_location="West Wing", created_by_id=cashier1.id)
        shift_d3_eve = Shift(id=str(uuid.uuid4()), cashier_id=cashier4.id, start_time=days_ago_3 + timedelta(hours=16), end_time=days_ago_3 + timedelta(hours=22), start_cash=150.00, status="closed", terminal_id="terminal_01", store_location="West Wing", created_by_id=cashier4.id)

        # Day 2 shifts
        shift_d2_morn = Shift(id=str(uuid.uuid4()), cashier_id=cashier1.id, start_time=days_ago_2 + timedelta(hours=8), end_time=days_ago_2 + timedelta(hours=16), start_cash=150.00, status="closed", terminal_id="terminal_01", store_location="West Wing", created_by_id=cashier1.id)
        shift_d2_eve = Shift(id=str(uuid.uuid4()), cashier_id=cashier2.id, start_time=days_ago_2 + timedelta(hours=16), end_time=days_ago_2 + timedelta(hours=22), start_cash=150.00, status="closed", terminal_id="terminal_01", store_location="West Wing", created_by_id=cashier2.id)

        # Day 1 shifts
        shift_d1_morn = Shift(id=str(uuid.uuid4()), cashier_id=cashier3.id, start_time=days_ago_1 + timedelta(hours=8), end_time=days_ago_1 + timedelta(hours=16), start_cash=150.00, status="closed", terminal_id="terminal_02", store_location="Central Aisle", created_by_id=cashier3.id)
        shift_d1_eve = Shift(id=str(uuid.uuid4()), cashier_id=cashier4.id, start_time=days_ago_1 + timedelta(hours=16), end_time=days_ago_1 + timedelta(hours=22), start_cash=150.00, status="closed", terminal_id="terminal_02", store_location="Central Aisle", created_by_id=cashier4.id)

        # Today's Shift (Active Open Shift with Alert)
        shift_today = Shift(id=str(uuid.uuid4()), cashier_id=cashier1.id, start_time=now - timedelta(hours=4), start_cash=150.00, status="open", terminal_id="terminal_01", store_location="West Wing", created_by_id=cashier1.id)

        all_shifts = [
            shift_d5_morn, shift_d5_eve,
            shift_d4_morn, shift_d4_eve,
            shift_d3_morn, shift_d3_eve,
            shift_d2_morn, shift_d2_eve,
            shift_d1_morn, shift_d1_eve,
            shift_today
        ]
        db.session.add_all(all_shifts)
        db.session.flush()

        print("Defining historical sales transactions...")
        sales_to_create = [
            # --- DAY 5 ---
            {
                "invoice": "INV-2026-0001",
                "time": days_ago_5 + timedelta(hours=9, minutes=15),
                "cashier": cashier1, "customer": john, "payment": "cash",
                "discount": None, "shift": shift_d5_morn,
                "items": [(cola, 10.0)]
            },
            {
                "invoice": "INV-2026-0002",
                "time": days_ago_5 + timedelta(hours=11, minutes=30),
                "cashier": cashier1, "customer": alice, "payment": "card",
                "discount": "SUMMER10", "shift": shift_d5_morn,
                "items": [(milk, 10.0), (apples, 1.666)]
            },
            {
                "invoice": "INV-2026-0003",
                "time": days_ago_5 + timedelta(hours=14, minutes=45),
                "cashier": cashier1, "customer": None, "payment": "cash",
                "discount": "WELCOME5", "shift": shift_d5_morn,
                "items": [(chips, 9.0)]
            },
            {
                "invoice": "INV-2026-0004",
                "time": days_ago_5 + timedelta(hours=17, minutes=20),
                "cashier": cashier2, "customer": david, "payment": "card",
                "discount": None, "shift": shift_d5_eve,
                "items": [(bread, 2.0), (cookie, 5.0)]
            },
            {
                "invoice": "INV-2026-0005",
                "time": days_ago_5 + timedelta(hours=19, minutes=15),
                "cashier": cashier2, "customer": emily, "payment": "mobile_pay",
                "discount": None, "shift": shift_d5_eve,
                "items": [(tshirt, 1.0), (cable, 1.0)]
            },
            {
                "invoice": "INV-2026-0006",
                "time": days_ago_5 + timedelta(hours=21, minutes=5),
                "cashier": cashier2, "customer": None, "payment": "cash",
                "discount": None, "shift": shift_d5_eve,
                "items": [(cola, 5.0), (chips, 3.0)]
            },
            
            # --- DAY 4 ---
            {
                "invoice": "INV-2026-0007",
                "time": days_ago_4 + timedelta(hours=10, minutes=30),
                "cashier": manager1, "customer": bob, "payment": "cash",
                "discount": None, "shift": shift_d4_morn,
                "items": [(cable, 10.0), (apples, 12.887)]
            },
            {
                "invoice": "INV-2026-0008",
                "time": days_ago_4 + timedelta(hours=12, minutes=45),
                "cashier": manager1, "customer": john, "payment": "card",
                "discount": None, "shift": shift_d4_morn,
                "items": [(chips, 30.0)]
            },
            {
                "invoice": "INV-2026-0009",
                "time": days_ago_4 + timedelta(hours=15, minutes=15),
                "cashier": manager1, "customer": None, "payment": "cash",
                "discount": None, "shift": shift_d4_morn,
                "items": [(cola, 12.0), (bananas, 5.500)]
            },
            {
                "invoice": "INV-2026-0010",
                "time": days_ago_4 + timedelta(hours=18, minutes=30),
                "cashier": cashier3, "customer": michael, "payment": "card",
                "discount": "SPRING20", "shift": shift_d4_eve,
                "items": [(bread, 4.0), (milk, 5.0)]
            },
            {
                "invoice": "INV-2026-0011",
                "time": days_ago_4 + timedelta(hours=20, minutes=45),
                "cashier": cashier3, "customer": alice, "payment": "cash",
                "discount": None, "shift": shift_d4_eve,
                "items": [(cookie, 12.0), (cola, 6.0)]
            },

            # --- DAY 3 ---
            {
                "invoice": "INV-2026-0012",
                "time": days_ago_3 + timedelta(hours=13, minutes=15),
                "cashier": cashier1, "customer": None, "payment": "cash",
                "discount": None, "shift": shift_d3_morn,
                "items": [(milk, 37.0)]
            },
            {
                "invoice": "INV-2026-0013",
                "time": days_ago_3 + timedelta(hours=15, minutes=30),
                "cashier": cashier1, "customer": david, "payment": "card",
                "discount": None, "shift": shift_d3_morn,
                "items": [(bread, 3.0), (apples, 4.200)]
            },
            {
                "invoice": "INV-2026-0014",
                "time": days_ago_3 + timedelta(hours=17, minutes=45),
                "cashier": cashier4, "customer": emily, "payment": "mobile_pay",
                "discount": "WINTER15", "shift": shift_d3_eve,
                "items": [(tshirt, 2.0)]
            },
            {
                "invoice": "INV-2026-0015",
                "time": days_ago_3 + timedelta(hours=19, minutes=50),
                "cashier": cashier4, "customer": bob, "payment": "cash",
                "discount": None, "shift": shift_d3_eve,
                "items": [(chips, 15.0), (cola, 8.0)]
            },
            {
                "invoice": "INV-2026-0016",
                "time": days_ago_3 + timedelta(hours=21, minutes=10),
                "cashier": cashier4, "customer": None, "payment": "card",
                "discount": None, "shift": shift_d3_eve,
                "items": [(cookie, 10.0), (milk, 2.0)]
            },

            # --- DAY 2 ---
            {
                "invoice": "INV-2026-0017",
                "time": days_ago_2 + timedelta(hours=10, minutes=0),
                "cashier": cashier1, "customer": bob, "payment": "cash",
                "discount": None, "shift": shift_d2_morn,
                "items": [(apples, 92.376)]
            },
            {
                "invoice": "INV-2026-0018",
                "time": days_ago_2 + timedelta(hours=14, minutes=0),
                "cashier": cashier1, "customer": alice, "payment": "cash",
                "discount": None, "shift": shift_d2_morn,
                "items": [(bananas, 230.944)]
            },
            {
                "invoice": "INV-2026-0019",
                "time": days_ago_2 + timedelta(hours=18, minutes=15),
                "cashier": cashier2, "customer": john, "payment": "card",
                "discount": None, "shift": shift_d2_eve,
                "items": [(tshirt, 1.0), (bread, 1.0)]
            },
            {
                "invoice": "INV-2026-0020",
                "time": days_ago_2 + timedelta(hours=20, minutes=30),
                "cashier": cashier2, "customer": None, "payment": "cash",
                "discount": None, "shift": shift_d2_eve,
                "items": [(chips, 10.0), (cookie, 6.0)]
            },

            # --- DAY 1 ---
            {
                "invoice": "INV-2026-0021",
                "time": days_ago_1 + timedelta(hours=9, minutes=45),
                "cashier": cashier3, "customer": emily, "payment": "card",
                "discount": None, "shift": shift_d1_morn,
                "items": [(cable, 2.0), (bread, 2.0)]
            },
            {
                "invoice": "INV-2026-0022",
                "time": days_ago_1 + timedelta(hours=13, minutes=30),
                "cashier": cashier3, "customer": michael, "payment": "cash",
                "discount": "WELCOME5", "shift": shift_d1_morn,
                "items": [(cola, 15.0), (chips, 12.0)]
            },
            {
                "invoice": "INV-2026-0023",
                "time": days_ago_1 + timedelta(hours=17, minutes=10),
                "cashier": cashier4, "customer": david, "payment": "cash",
                "discount": None, "shift": shift_d1_eve,
                "items": [(apples, 10.500), (bananas, 8.200)]
            },
            {
                "invoice": "INV-2026-0024",
                "time": days_ago_1 + timedelta(hours=19, minutes=40),
                "cashier": cashier4, "customer": john, "payment": "card",
                "discount": "EMP10", "shift": shift_d1_eve,
                "items": [(tshirt, 3.0)]
            },
            {
                "invoice": "INV-2026-0025",
                "time": days_ago_1 + timedelta(hours=21, minutes=15),
                "cashier": cashier4, "customer": None, "payment": "cash",
                "discount": None, "shift": shift_d1_eve,
                "items": [(cola, 4.0), (chips, 4.0)]
            },

            # --- TODAY (ACTIVE SHIFT) ---
            {
                "invoice": "INV-2026-0026",
                "time": now - timedelta(hours=2),
                "cashier": cashier1, "customer": john, "payment": "cash",
                "discount": None, "shift": shift_today,
                "items": [(cable, 2.0), (apples, 276.633)]
            }
        ]

        print("Calculating totals, saving sales, and writing inventory logs...")
        db_sales = []
        sales_changes = {} # product_id -> sum of -qty

        for s_data in sales_to_create:
            subtotal = 0.0
            for prod, qty in s_data["items"]:
                subtotal += float(prod.price) * qty
                sales_changes[prod.id] = sales_changes.get(prod.id, 0.0) - qty

            discount_val = 0.0
            if s_data["discount"]:
                disc = next((d for d in [spring_promo, summer_promo, welcome_promo, winter_promo, emp_promo] if d.code == s_data["discount"]), None)
                if disc:
                    if disc.discount_type == "percent":
                        discount_val = round(subtotal * (float(disc.value) / 100.0), 2)
                    else:
                        discount_val = float(disc.value)

            taxable_amount = max(0.0, subtotal - discount_val)
            tax = round(taxable_amount * 0.0825, 2)
            total = round(taxable_amount + tax, 2)

            sale = Sale(
                invoice_number=s_data["invoice"],
                subtotal=subtotal,
                discount=discount_val,
                tax=tax,
                total=total,
                payment_method=s_data["payment"],
                cashier_id=s_data["cashier"].id,
                customer_id=s_data["customer"].id if s_data["customer"] else None,
                shift_id=s_data["shift"].id if s_data["shift"] else None,
                created_at=s_data["time"],
                terminal_id=s_data["shift"].terminal_id,
                store_location=s_data["shift"].store_location,
                created_by_id=s_data["cashier"].id
            )
            db.session.add(sale)
            db_sales.append(sale)
            db.session.flush()

            # Loyalty points calculation
            if s_data["customer"]:
                s_data["customer"].loyalty_points += int(total)

            # Create SaleItems and InventoryLogs for each sale item
            for prod, qty in s_data["items"]:
                unit_price = float(prod.price)
                total_price = round(unit_price * qty, 2)

                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=prod.id,
                    quantity=qty,
                    unit_price=unit_price,
                    total_price=total_price,
                    created_at=s_data["time"]
                )
                db.session.add(sale_item)

                # Inventory sale deduction log
                log = InventoryLog(
                    product_id=prod.id,
                    quantity_changed=-qty,
                    reason="sale",
                    reference_id=s_data["invoice"],
                    created_at=s_data["time"],
                    notes=f"POS Sale. Invoice: {s_data['invoice']}",
                    created_by_id=s_data["cashier"].id
                )
                db.session.add(log)

        print("Writing manual audit logs, damage adjustments, and returns...")
        custom_logs_to_add = [
            # Cola damage adjustment
            {
                "product": cola, "qty": -2.0, "reason": "damage",
                "ref": "ADJ-2026-0001", "time": days_ago_3 + timedelta(hours=14),
                "notes": "Damaged bottle found during stock shelf audit", "user": manager1
            },
            # Milk return from customer
            {
                "product": milk, "qty": 3.0, "reason": "return",
                "ref": "RET-2026-0001", "time": days_ago_2 + timedelta(hours=15),
                "notes": "Unused return by customer - items verified and restocked", "user": cashier1
            },
            # Chips stock replenishment PO
            {
                "product": chips, "qty": 50.0, "reason": "restock",
                "ref": "PO-2026-0001", "time": days_ago_1 + timedelta(hours=10),
                "notes": "Weekly inventory delivery replenishment top-up", "user": manager2
            }
        ]

        custom_changes = {}
        for c_log in custom_logs_to_add:
            custom_changes[c_log["product"].id] = custom_changes.get(c_log["product"].id, 0.0) + c_log["qty"]
            
            db.session.add(InventoryLog(
                product_id=c_log["product"].id,
                quantity_changed=c_log["qty"],
                reason=c_log["reason"],
                reference_id=c_log["ref"],
                created_at=c_log["time"],
                notes=c_log["notes"],
                created_by_id=c_log["user"].id
            ))

        print("Computing and seeding initial restocks to make logs perfectly balance...")
        products = [cola, milk, chips, apples, bananas, cable, bread, cookie, tshirt]
        for prod in products:
            total_sold_qty = -sales_changes.get(prod.id, 0.0)
            total_custom_qty = custom_changes.get(prod.id, 0.0)
            
            # initial_qty = final_stock + total_sold - total_custom
            initial_qty = float(prod.stock_quantity) + total_sold_qty - total_custom_qty
            
            db.session.add(InventoryLog(
                product_id=prod.id,
                quantity_changed=initial_qty,
                reason="restock",
                reference_id="INITIAL-STOCK-LOAD",
                created_at=days_ago_5 - timedelta(days=1),
                notes="Initial setup stock loading of inventory ledger",
                created_by_id=admin.id
            ))

        print("Programmatically updating closed shifts cash drawer totals and variances...")
        for shift in all_shifts:
            if shift.status == "closed":
                shift_sales = [s for s in db_sales if s.shift_id == shift.id]
                cash_collected = sum(float(s.total) for s in shift_sales if s.payment_method == "cash")
                
                variance = 0.0
                if shift == shift_d2_morn:
                    variance = -5.00  # Shift 2 morning had a $5 shortage!
                    
                shift.end_cash = float(shift.start_cash) + cash_collected + variance

        db.session.commit()
        print("Historical record database seeded successfully across all 10 tables, preserving migration schema state!")

if __name__ == '__main__':
    seed_historical_database()
