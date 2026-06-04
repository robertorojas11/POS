import os
from dotenv import load_dotenv

# Load env before importing other files
load_dotenv()

from app import create_app, db
from app.models.user import User, UserType
from app.models.product import Category, Product
from app.models.customer import Customer

def seed_database():
    app = create_app(os.getenv('FLASK_CONFIG', 'default'))
    with app.app_context():
        print("Recreating database tables...")
        db.drop_all()
        db.create_all()

        print("Seeding user types...")
        admin_type = UserType(id=1, name="Admin")
        manager_type = UserType(id=2, name="Manager")
        operator_type = UserType(id=3, name="Operator")
        db.session.add_all([admin_type, manager_type, operator_type])
        db.session.flush() # ensure user types are written to get their IDs

        print("Seeding users...")
        # Create admin
        admin = User(username="admin", email="admin@apexpos.com", user_type_id=admin_type.id)
        admin.set_password("admin")
        db.session.add(admin)

        # Create manager
        manager = User(username="manager1", email="manager1@apexpos.com", user_type_id=manager_type.id)
        manager.set_password("securepassword")
        db.session.add(manager)

        # Create operator
        cashier = User(username="cashier1", email="cashier1@apexpos.com", user_type_id=operator_type.id)
        cashier.set_password("securepassword")
        db.session.add(cashier)

        print("Seeding product categories...")
        beverages = Category(name="Beverages", description="Soft drinks, coffee, tea, and juice")
        snacks = Category(name="Snacks", description="Chips, candy, pretzels, and cookies")
        electronics = Category(name="Electronics", description="Cables, chargers, and small accessories")
        apparel = Category(name="Apparel", description="Shirts, hats, and merchandise")
        
        db.session.add_all([beverages, snacks, electronics, apparel])
        db.session.flush() # populate category IDs

        print("Seeding products...")
        products = [
            Product(sku="BEV-COLA-01", barcode="012000000133", name="Classic Cola 12oz", description="Refreshing carbonated cola", price=1.99, cost_price=0.60, stock_quantity=120, min_stock_level=15, category_id=beverages.id),
            Product(sku="BEV-COFF-02", barcode="043000045321", name="Organic Dark Coffee", description="Rich roasted coffee beans brew", price=3.49, cost_price=1.10, stock_quantity=45, min_stock_level=10, category_id=beverages.id),
            Product(sku="SNK-CHIP-01", barcode="028400091496", name="Sea Salt Potato Chips", description="Crispy salted potato chips", price=2.99, cost_price=1.20, stock_quantity=3, min_stock_level=10, category_id=snacks.id), # Low stock!
            Product(sku="SNK-CHOC-02", barcode="034000002451", name="Milk Chocolate Bar", description="Creamy milk chocolate block", price=1.79, cost_price=0.75, stock_quantity=80, min_stock_level=15, category_id=snacks.id),
            Product(sku="ELC-USBC-01", barcode="884838291044", name="Braided USB-C Cable 6ft", description="High-speed charging USB type C cable", price=9.99, cost_price=3.50, stock_quantity=25, min_stock_level=5, category_id=electronics.id),
            Product(sku="APP-TSHR-01", barcode="729381029381", name="ApexPOS Logo T-Shirt", description="100% Cotton branded graphic tee", price=19.99, cost_price=8.00, stock_quantity=15, min_stock_level=3, category_id=apparel.id)
        ]
        
        db.session.add_all(products)
        
        print("Seeding customer accounts...")
        customer = Customer(name="John Doe", phone="555-0199", email="john.doe@example.com", loyalty_points=120)
        db.session.add(customer)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
