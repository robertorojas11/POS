from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User, UserType

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
    user = User.query.get(int(current_user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200
