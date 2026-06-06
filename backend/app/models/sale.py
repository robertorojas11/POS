from datetime import datetime
from app.extensions import db

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    discount = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(32), default='cash', nullable=False)  # cash, card, mobile_pay, split
    cash_amount = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    card_amount = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    mobile_amount = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    cashier_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    shift_id = db.Column(db.String(36), db.ForeignKey('shifts.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    terminal_id = db.Column(db.String(64), default='terminal_01')
    store_location = db.Column(db.String(128), default='Main Store')
    device_ip = db.Column(db.String(45), default='127.0.0.1')
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    cashier = db.relationship('User', back_populates='sales', foreign_keys=[cashier_id])
    customer = db.relationship('Customer', back_populates='sales')
    shift = db.relationship('Shift', back_populates='sales')
    items = db.relationship('SaleItem', back_populates='sale', lazy='subquery', cascade='all, delete-orphan')
    creator = db.relationship('User', foreign_keys=[created_by_id])
    updater = db.relationship('User', foreign_keys=[updated_by_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'subtotal': float(self.subtotal),
            'tax': float(self.tax),
            'discount': float(self.discount),
            'total': float(self.total),
            'payment_method': self.payment_method,
            'cash_amount': float(self.cash_amount),
            'card_amount': float(self.card_amount),
            'mobile_amount': float(self.mobile_amount),
            'cashier_id': self.cashier_id,
            'cashier_name': self.cashier.username if self.cashier else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'shift_id': self.shift_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'terminal_id': self.terminal_id,
            'store_location': self.store_location,
            'device_ip': self.device_ip,
            'created_by_id': self.created_by_id,
            'updated_by_id': self.updated_by_id,
            'items': [item.to_dict() for item in self.items]
        }


class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Numeric(10, 3), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    sale = db.relationship('Sale', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown Product',
            'product_sku': self.product.sku if self.product else '',
            'quantity': float(self.quantity),
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Discount(db.Model):
    __tablename__ = 'discounts'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    discount_type = db.Column(db.String(16), default='fixed', nullable=False)  # fixed, percent
    value = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by_id])
    updater = db.relationship('User', foreign_keys=[updated_by_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'discount_type': self.discount_type,
            'value': float(self.value),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by_id': self.created_by_id,
            'updated_by_id': self.updated_by_id
        }
