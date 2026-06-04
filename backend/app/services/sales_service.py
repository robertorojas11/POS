from datetime import datetime
import uuid
from app.extensions import db
from app.models.product import Product
from app.models.inventory import InventoryLog
from app.models.sale import Sale, SaleItem
from app.models.customer import Customer
from app.services.redis_service import RedisService

class SalesService:
    @staticmethod
    def generate_invoice_number():
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_suffix = str(uuid.uuid4().hex[:6]).upper()
        return f"INV-{timestamp}-{unique_suffix}"

    @staticmethod
    def process_checkout(cashier_id, cart_items, payment_method, customer_id=None, discount=0.00, tax_rate=0.0825):
        """
        Executes the atomic checkout operation:
        1. Validates stock levels.
        2. Creates Sale and SaleItem records.
        3. Updates stock quantities.
        4. Writes audit log to InventoryLogs.
        5. Computes customer loyalty points.
        6. Invalidates Redis cache.
        7. Publishes real-time sale completed event.
        """
        try:
            from app.models.shift import Shift
            
            # Verify cashier has an active open shift session
            active_shift = db.session.query(Shift).filter(
                Shift.cashier_id == cashier_id,
                Shift.status == 'open'
            ).first()
            if not active_shift:
                raise ValueError("No open cash shift found. Cashier must start a turn session first.")
                
            # Generate unique invoice number
            invoice_num = SalesService.generate_invoice_number()
            
            subtotal = 0.00
            items_to_save = []
            products_to_update = []
            inventory_logs = []
            
            # Loop through cart items and process
            for item in cart_items:
                product_id = item.get('product_id')
                qty = item.get('quantity', 1)
                
                # Lock row for update to prevent race conditions in multi-register setups
                product = db.session.query(Product).filter(Product.id == product_id).with_for_update().first()
                
                if not product or not product.is_active:
                    raise ValueError(f"Product ID {product_id} is inactive or does not exist.")
                    
                if product.stock_quantity < qty:
                    raise ValueError(f"Insufficient stock for {product.name}. Required: {qty}, Available: {product.stock_quantity}")
                
                # Calculate item pricing
                unit_price = float(product.price)
                total_price = unit_price * qty
                subtotal += total_price
                
                # Subtract stock
                product.stock_quantity -= qty
                products_to_update.append(product)
                
                # Keep reference for SaleItem creation
                items_to_save.append({
                    'product_id': product.id,
                    'quantity': qty,
                    'unit_price': unit_price,
                    'total_price': total_price
                })
                
                # Add to inventory audit log
                inventory_logs.append(InventoryLog(
                    product_id=product.id,
                    quantity_changed=-qty,
                    reason='sale',
                    reference_id=invoice_num,
                    notes=f"POS Sale. Invoice: {invoice_num}"
                ))
            
            # Subtotal, discount, tax, total calculation
            discount_val = float(discount)
            taxable_amount = max(0.0, subtotal - discount_val)
            tax_val = taxable_amount * tax_rate
            total_val = taxable_amount + tax_val
            
            # Handle Customer loyalty points (1 point per dollar spent)
            customer = None
            if customer_id:
                customer = db.session.query(Customer).filter(Customer.id == customer_id).with_for_update().first()
                if customer:
                    points_earned = int(total_val)
                    customer.loyalty_points += points_earned
            
            # Create Sale object
            sale = Sale(
                invoice_number=invoice_num,
                subtotal=subtotal,
                discount=discount_val,
                tax=tax_val,
                total=total_val,
                payment_method=payment_method,
                cashier_id=cashier_id,
                customer_id=customer_id,
                shift_id=active_shift.id
            )
            db.session.add(sale)
            db.session.flush()  # gets sale.id
            
            # Add SaleItems
            for item in items_to_save:
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    total_price=item['total_price']
                )
                db.session.add(sale_item)
                
            # Add inventory logs
            for log in inventory_logs:
                db.session.add(log)
                
            # Commit atomic transaction
            db.session.commit()
            
            # Post-commit cache and event publishing
            RedisService.invalidate_products_cache()
            
            sale_dict = sale.to_dict()
            RedisService.publish_sale_event(sale_dict)
            
            return sale_dict
            
        except Exception as e:
            db.session.rollback()
            raise e
