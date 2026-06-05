from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User, UserType
from app.utils.permissions import requires_user_type
import string
import random

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    user_type_id = data.get('user_type_id')
    if not user_type_id:
        role = str(data.get('role', 'operator')).lower()
        if role in ('admin', '1'):
            user_type_id = 1
        elif role in ('manager', '2'):
            user_type_id = 2
        elif role in ('operator', 'cashier', '3'):
            user_type_id = 3
        else:
            user_type_id = 3  # default to operator
            
    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400
        
    # Verify user type exists
    ut = db.session.get(UserType, user_type_id)
    if not ut:
        return jsonify({"error": "Invalid user type ID"}), 400
        
    user = User(username=username, email=email, user_type_id=user_type_id)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully", "user": user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
        
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401
        
    if not user.is_active:
        return jsonify({"error": "Account is inactive"}), 403
        
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))
    if not user:
        return jsonify({"error": "User session is invalid. Please log in again."}), 401
    return jsonify(user.to_dict()), 200


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)
    
    if not current_user:
        return jsonify({"error": "User session is invalid. Please log in again."}), 401
        
    if current_user.user_type.name not in ('Admin', 'Manager'):
        return jsonify({"error": "Access denied"}), 403
        
    if current_user.user_type.name == 'Admin':
        users = User.query.all()
    else:
        # Managers only see Operators (id=3)
        users = User.query.filter_by(user_type_id=3).all()
        
    return jsonify([u.to_dict() for u in users]), 200


@auth_bp.route('/employees', methods=['POST'])
@jwt_required()
@requires_user_type('Admin')
def register_employee():
    data = request.get_json() or {}
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    second_last_name = data.get('second_last_name')
    email = data.get('email')
    contact_phone = data.get('contact_phone')
    user_type_id = data.get('user_type_id', 3)  # default to 3 (Operator/Cashier)
    store_id = data.get('store_id')
    
    if not first_name or not last_name or not email or not store_id:
        return jsonify({"error": "First name, last name, email, and store assignment are required"}), 400
        
    from app.models.store import Store
    store = db.session.get(Store, store_id)
    if not store:
        return jsonify({"error": "Store assignment is invalid"}), 400
        
    # Check if email is already taken
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email is already in use"}), 400
        
    # Generate username: firstname.first_surname_letter.xy
    fn = first_name.strip().lower().replace(" ", "")
    ln = last_name.strip().lower().replace(" ", "")
    s_code = store.code.strip().lower()
    
    chars = string.ascii_lowercase + string.digits
    rand_chars = "".join(random.choices(chars, k=2))
    username = f"{fn}.{ln[0]}.{s_code}{rand_chars}"
    
    while User.query.filter_by(username=username).first():
        rand_chars = "".join(random.choices(chars, k=2))
        username = f"{fn}.{ln[0]}.{s_code}{rand_chars}"
        
    temp_pass = "Temp" + "".join(random.choices(string.digits, k=4))
    
    # Create employee user
    user = User(
        username=username,
        email=email,
        user_type_id=user_type_id,
        first_name=first_name,
        last_name=last_name,
        second_last_name=second_last_name,
        contact_phone=contact_phone,
        store_id=store_id,
        must_change_password=True
    )
    user.set_password(temp_pass)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "Employee registered successfully",
        "user": user.to_dict(),
        "temporal_password": temp_pass
    }), 201


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = int(get_jwt_identity())
    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({"error": "User session is invalid. Please log in again."}), 401
    data = request.get_json() or {}
    new_password = data.get('new_password')
    
    if not new_password or len(new_password) < 4:
        return jsonify({"error": "Password must be at least 4 characters long"}), 400
        
    user.set_password(new_password)
    user.must_change_password = False
    db.session.commit()
    
    return jsonify({"message": "Password updated successfully"}), 200


@auth_bp.route('/employees/<int:user_id>', methods=['PUT'])
@jwt_required()
@requires_user_type('Admin')
def update_employee(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Employee not found"}), 404
        
    data = request.get_json() or {}
    email = data.get('email')
    
    if email and email != user.email:
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email is already in use by another user"}), 400
            
    # Update fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'second_last_name' in data:
        user.second_last_name = data['second_last_name']
    if 'email' in data:
        user.email = data['email']
    if 'contact_phone' in data:
        user.contact_phone = data['contact_phone']
    if 'user_type_id' in data:
        user.user_type_id = int(data['user_type_id'])
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
        
    if 'store_id' in data:
        store_id = data['store_id']
        if store_id == '' or store_id is None:
            user.store_id = None
        else:
            from app.models.store import Store
            store = db.session.get(Store, int(store_id))
            if not store:
                return jsonify({"error": "Assigned store is invalid"}), 400
            user.store_id = int(store_id)
            
    user.updated_by_id = int(get_jwt_identity())
    db.session.commit()
    return jsonify(user.to_dict()), 200


@auth_bp.route('/employees/<int:user_id>', methods=['DELETE'])
@jwt_required()
@requires_user_type('Admin')
def delete_employee(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Employee not found"}), 404
        
    current_admin_id = int(get_jwt_identity())
    if user.id == current_admin_id:
        return jsonify({"error": "You cannot delete your own admin account"}), 400
        
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Employee deleted successfully"}), 200
