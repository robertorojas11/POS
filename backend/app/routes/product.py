from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.product import Product, Category
from app.utils.permissions import requires_user_type

product_bp = Blueprint('product', __name__)

@product_bp.route('', methods=['GET'])
@jwt_required()
def get_products():
    search = request.args.get('search', '')
    category_id = request.args.get('category_id')
    barcode = request.args.get('barcode', '')
    
    query = Product.query.filter(Product.is_active == True)
    
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) | 
            (Product.sku.ilike(f'%{search}%'))
        )
    if category_id:
        query = query.filter(Product.category_id == int(category_id))
    if barcode:
        query = query.filter(Product.barcode == barcode)
        
    products = query.all()
    return jsonify([p.to_dict() for p in products]), 200


@product_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200


@product_bp.route('/barcode/<string:barcode>', methods=['GET'])
@jwt_required()
def get_product_by_barcode(barcode):
    product = Product.query.filter_by(barcode=barcode, is_active=True).first()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict()), 200


@product_bp.route('', methods=['POST'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def create_product():
    # In a real app, verify admin/manager role here
    data = request.get_json() or {}
    sku = data.get('sku')
    name = data.get('name')
    price = data.get('price')
    cost_price = data.get('cost_price')
    
    if not all([sku, name, price, cost_price]):
        return jsonify({"error": "SKU, Name, Price, and Cost Price are required"}), 400
        
    if Product.query.filter_by(sku=sku).first():
        return jsonify({"error": "Product with this SKU already exists"}), 400
        
    product = Product(
        sku=sku,
        barcode=data.get('barcode'),
        name=name,
        description=data.get('description'),
        price=price,
        cost_price=cost_price,
        stock_quantity=data.get('stock_quantity', 0),
        min_stock_level=data.get('min_stock_level', 5),
        category_id=data.get('category_id')
    )
    
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json() or {}
    
    for field in ['name', 'barcode', 'description', 'price', 'cost_price', 'stock_quantity', 'min_stock_level', 'category_id', 'is_active']:
        if field in data:
            setattr(product, field, data[field])
            
    db.session.commit()
    return jsonify(product.to_dict()), 200


@product_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories]), 200


@product_bp.route('/categories', methods=['POST'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def create_category():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({"error": "Category name required"}), 400
        
    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "Category already exists"}), 400
        
    category = Category(name=name, description=data.get('description'))
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201
