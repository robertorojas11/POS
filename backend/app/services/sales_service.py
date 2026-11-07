from datetime import datetime
from decimal import Decimal
import uuid
from flask import current_app
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.product import Product
from app.models.inventory import InventoryLog
from app.models.sale import Sale, SaleItem, Discount
from app.models.customer import Customer
from app.models.shift import Shift
from app.services.redis_service import RedisService
from app.utils.validation import to_decimal, money

PAYMENT_METHODS = ('cash', 'card', 'mobile_pay', 'split')
MANUAL_DISCOUNT_ROLES = ('Admin', 'Manager')


class SalesService:
    @staticmethod
    def generate_invoice_number():
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"INV-{timestamp}-{uuid.uuid4().hex[:6].upper()}"

    @staticmethod
    def _merge_items(cart_items):
        """Validate cart lines and merge duplicates. Sorted by product id so concurrent
        checkouts lock rows in the same order (no deadlocks)."""
        if not isinstance(cart_items, list) or not cart_items:
            raise ValueError("Cart is empty")
        merged = {}
        for item in cart_items:
            try:
                product_id = int(item.get('product_id'))
            except (TypeError, ValueError, AttributeError):
                raise ValueError("Invalid product in cart")
            qty = to_decimal(item.get('quantity', 1), 'quantity', allow_zero=False)
            merged[product_id] = merged.get(product_id, Decimal('0')) + qty
        return sorted(merged.items())

    @staticmethod
    def _discount_amount(subtotal, discount, discount_code, user_type):
        if discount_code:
            code = db.session.query(Discount).filter_by(
                code=str(discount_code).strip().upper(), is_active=True).first()
            if not code:
                raise ValueError("Invalid or inactive discount code")
            if code.discount_type == 'percent':
                return money(subtotal * code.value / 100)
            return min(subtotal, money(code.value))
        amount = to_decimal(discount or 0, 'discount')
        if amount > 0 and user_type not in MANUAL_DISCOUNT_ROLES:
            raise ValueError("Manual discounts require a Manager or Admin. Use a discount code.")
        return min(subtotal, money(amount))

    @staticmethod
    def _split_amounts(payment_method, payment_details, total):
        zero = Decimal('0.00')
        if payment_method == 'cash':
            return total, zero, zero
        if payment_method == 'card':
            return zero, total, zero
        if payment_method == 'mobile_pay':
            return zero, zero, total
        details = payment_details or {}
        cash = money(to_decimal(details.get('cash', 0), 'cash'))
        card = money(to_decimal(details.get('card', 0), 'card'))
        mobile = money(to_decimal(details.get('mobile_pay', 0), 'mobile_pay'))
        if cash + card + mobile != total:
            raise ValueError(f"Split payments ({cash + card + mobile}) must add up to the total ({total})")
        return cash, card, mobile

    @staticmethod
    def process_checkout(cashier_id, cart_items, payment_method, customer_id=None, discount=0,
                         discount_code=None, payment_details=None, client_ref=None, user_type=None):
        """
        Atomic checkout. The server owns every number: prices, tax rate and discounts are computed
        here, never trusted from the client.
        client_ref makes the call idempotent: a retry (offline queue, double click) returns the
        sale already created instead of charging twice.
        """
        if payment_method not in PAYMENT_METHODS:
            raise ValueError(f"Invalid payment method. Use one of: {', '.join(PAYMENT_METHODS)}")

        if client_ref:
            existing = db.session.query(Sale).filter_by(client_ref=str(client_ref)).first()
            if existing:
                return existing.to_dict()

        try:
            lines = SalesService._merge_items(cart_items)

            # Locking the shift row also serialises checkout against "close shift"
            active_shift = db.session.query(Shift).filter(
                Shift.cashier_id == cashier_id, Shift.status == 'open'
            ).with_for_update().first()
            if not active_shift:
                raise ValueError("No open cash shift found. Cashier must start a turn session first.")

            invoice_num = SalesService.generate_invoice_number()
            subtotal = Decimal('0.00')
            sale_items = []
            logs = []

            for product_id, qty in lines:
                product = db.session.query(Product).filter(Product.id == product_id).with_for_update().first()
                if not product or not product.is_active:
                    raise ValueError(f"Product ID {product_id} is inactive or does not exist.")
                if qty % product.min_sale_qty != 0:
                    raise ValueError(f"{product.name} must be sold in steps of {product.min_sale_qty} {product.uom}")
                if product.stock_quantity < qty:
                    raise ValueError(f"Insufficient stock for {product.name}. Required: {qty}, Available: {product.stock_quantity}")

                line_total = money(product.price * qty)
                subtotal += line_total
                product.stock_quantity -= qty
                sale_items.append(SaleItem(product_id=product.id, quantity=qty,
                                           unit_price=product.price, total_price=line_total))
                logs.append(InventoryLog(product_id=product.id, quantity_changed=-qty, reason='sale',
                                         reference_id=invoice_num, notes=f"POS Sale. Invoice: {invoice_num}"))

            discount_val = SalesService._discount_amount(subtotal, discount, discount_code, user_type)
            taxable = subtotal - discount_val
            tax_val = money(taxable * current_app.config['TAX_RATE'])
            total_val = taxable + tax_val

            if customer_id:
                customer = db.session.query(Customer).filter(Customer.id == customer_id).with_for_update().first()
                if not customer:
                    raise ValueError("Customer not found")
                customer.loyalty_points += int(total_val)  # 1 point per currency unit

            cash, card, mobile = SalesService._split_amounts(payment_method, payment_details, total_val)

            sale = Sale(
                invoice_number=invoice_num, client_ref=client_ref and str(client_ref),
                subtotal=subtotal, discount=discount_val, tax=tax_val, total=total_val,
                payment_method=payment_method, cash_amount=cash, card_amount=card, mobile_amount=mobile,
                cashier_id=cashier_id, customer_id=customer_id, shift_id=active_shift.id,
                items=sale_items,
            )
            db.session.add(sale)
            db.session.add_all(logs)
            db.session.commit()
        except IntegrityError:
            # Two requests with the same client_ref raced: the other one won, return its sale
            db.session.rollback()
            existing = client_ref and db.session.query(Sale).filter_by(client_ref=str(client_ref)).first()
            if existing:
                return existing.to_dict()
            raise
        except Exception:
            db.session.rollback()
            raise

        RedisService.invalidate_products_cache(notify=False)  # stock changed; no catalog-wide reload
        sale_dict = sale.to_dict()
        RedisService.publish_sale_event(sale_dict)
        return sale_dict
