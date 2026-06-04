from datetime import datetime
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class UserType(db.Model):
    __tablename__ = 'user_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)  # Admin, Manager, Operator
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', use_alter=True, name='fk_user_types_creator'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id', use_alter=True, name='fk_user_types_updater'), nullable=True)
    
    # Relationships
    users = db.relationship('User', back_populates='user_type', foreign_keys='User.user_type_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by_id': self.created_by_id,
            'updated_by_id': self.updated_by_id
        }

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    user_type_id = db.Column(db.Integer, db.ForeignKey('user_types.id'), nullable=False, default=3) # Default to 3 (Operator)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)
    
    # Relationships
    user_type = db.relationship('UserType', back_populates='users', foreign_keys=[user_type_id])
    sales = db.relationship('Sale', back_populates='cashier', lazy='dynamic', foreign_keys='Sale.cashier_id')
    creator = db.relationship('User', foreign_keys=[created_by_id], remote_side=[id])
    updater = db.relationship('User', foreign_keys=[updated_by_id], remote_side=[id])
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'user_type_id': self.user_type_id,
            'user_type': self.user_type.name if self.user_type else None,
            'role': self.user_type.name.lower() if self.user_type else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by_id': self.created_by_id,
            'updated_by_id': self.updated_by_id,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_login_ip': self.last_login_ip
        }
