from datetime import datetime
from app.extensions import db

class InventoryLog(db.Model):
    __tablename__ = 'inventory_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_changed = db.Column(db.Integer, nullable=False)  # positive for stock-in, negative for stock-out/sale
    reason = db.Column(db.String(64), nullable=False)  # 'sale', 'restock', 'adjustment', 'damage', 'return'
    reference_id = db.Column(db.String(64))  # Sale invoice number, PO number, or custom ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.String(256))
    
    # Relationships
    product = db.relationship('Product', back_populates='inventory_logs')
    creator = db.relationship('User', foreign_keys=[created_by_id])
    updater = db.relationship('User', foreign_keys=[updated_by_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity_changed': self.quantity_changed,
            'reason': self.reason,
            'reference_id': self.reference_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by_id': self.created_by_id,
            'updated_by_id': self.updated_by_id,
            'notes': self.notes
        }
