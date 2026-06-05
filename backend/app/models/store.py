from datetime import datetime
from app.extensions import db

class Store(db.Model):
    __tablename__ = 'stores'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    code = db.Column(db.String(16), unique=True, nullable=False, index=True) # Store identifier (x in username formula)
    location = db.Column(db.String(128))
    address = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', use_alter=True, name='fk_stores_creator'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id', use_alter=True, name='fk_stores_updater'), nullable=True)
    
    # Relationships
    users = db.relationship('User', back_populates='store', lazy='dynamic', foreign_keys='User.store_id')
    creator = db.relationship('User', foreign_keys=[created_by_id])
    updater = db.relationship('User', foreign_keys=[updated_by_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'location': self.location,
            'address': self.address,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by_id': self.created_by_id,
            'updated_by_id': self.updated_by_id
        }
