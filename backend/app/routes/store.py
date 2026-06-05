from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.store import Store
from app.models.user import User
from app.utils.permissions import requires_user_type

store_bp = Blueprint('store', __name__)

@store_bp.route('', methods=['GET'])
@jwt_required()
def get_stores():
    stores = Store.query.all()
    return jsonify([s.to_dict() for s in stores]), 200

@store_bp.route('/<int:store_id>', methods=['GET'])
@jwt_required()
def get_store(store_id):
    store = Store.query.get_or_404(store_id)
    return jsonify(store.to_dict()), 200

@store_bp.route('', methods=['POST'])
@jwt_required()
@requires_user_type('Admin')
def create_store():
    data = request.get_json() or {}
    name = data.get('name')
    code = data.get('code')
    
    if not name or not code:
        return jsonify({"error": "Store name and code are required"}), 400
        
    if Store.query.filter((Store.name == name) | (Store.code == code)).first():
        return jsonify({"error": "Store with this name or code already exists"}), 400
        
    store = Store(
        name=name,
        code=code,
        location=data.get('location'),
        address=data.get('address')
    )
    db.session.add(store)
    db.session.commit()
    return jsonify(store.to_dict()), 201

@store_bp.route('/<int:store_id>', methods=['PUT'])
@jwt_required()
@requires_user_type('Admin')
def update_store(store_id):
    store = Store.query.get_or_404(store_id)
    data = request.get_json() or {}
    
    if 'name' in data:
        store.name = data['name']
    if 'code' in data:
        store.code = data['code']
    if 'location' in data:
        store.location = data['location']
    if 'address' in data:
        store.address = data['address']
        
    db.session.commit()
    return jsonify(store.to_dict()), 200

@store_bp.route('/<int:store_id>', methods=['DELETE'])
@jwt_required()
@requires_user_type('Admin')
def delete_store(store_id):
    store = Store.query.get_or_404(store_id)
    
    # Detach all users assigned to this store
    for user in store.users:
        user.store_id = None
        
    db.session.delete(store)
    db.session.commit()
    return jsonify({"message": "Store deleted successfully"}), 200
