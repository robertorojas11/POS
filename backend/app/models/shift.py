from datetime import datetime
import uuid
from app.extensions import db

class Shift(db.Model):
    __tablename__ = 'shifts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cashier_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    start_cash = db.Column(db.Numeric(10, 2), nullable=False)
    end_cash = db.Column(db.Numeric(10, 2), nullable=True)
    status = db.Column(db.String(16), default='open', nullable=False)  # open, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    terminal_id = db.Column(db.String(64), default='terminal_01')
    store_location = db.Column(db.String(128), default='Main Store')
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    cashier = db.relationship('User', backref=db.backref('shifts_list', lazy='dynamic'), foreign_keys=[cashier_id])
    sales = db.relationship('Sale', back_populates='shift', lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[created_by_id])
    updater = db.relationship('User', foreign_keys=[updated_by_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'cashier_id': self.cashier_id,
            'cashier_name': self.cashier.username if self.cashier else None,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'start_cash': float(self.start_cash),
            'end_cash': float(self.end_cash) if self.end_cash is not None else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'terminal_id': self.terminal_id,
            'store_location': self.store_location,
            'created_by_id': self.created_by_id,
            'updated_by_id': self.updated_by_id
        }
