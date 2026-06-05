from flask import Blueprint, jsonify, request, Response
import json
from flask_jwt_extended import jwt_required
from app.models.product import Product, Category
from app.extensions import db, redis_client
from app.utils.permissions import requires_user_type
from app.services.redis_service import RedisService

product_bp = Blueprint('product', __name__)

@product_bp.route('', methods=['GET'])
@jwt_required()
def get_products():
    search = request.args.get('search', '')
    category_id = request.args.get('category_id')
    barcode = request.args.get('barcode', '')
    terminal_id = request.headers.get('X-Terminal-Id') or request.args.get('terminal_id') or 'default'
    
    is_full_catalog = not any([search, category_id, barcode])
    if is_full_catalog:
        cached = RedisService.get_cached_products(terminal_id)
        if cached:
            return jsonify(cached), 200
            
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
    products_list = [p.to_dict() for p in products]
    
    if is_full_catalog:
        RedisService.set_cached_products(products_list, terminal_id)
        
    return jsonify(products_list), 200


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
        
    barcode = data.get('barcode')
    if barcode == '' or barcode is None:
        barcode = None
        
    category_id = data.get('category_id')
    if category_id == '' or category_id is None:
        category_id = None
    else:
        category_id = int(category_id)
        
    product = Product(
        sku=sku,
        barcode=barcode,
        name=name,
        description=data.get('description'),
        price=float(price),
        cost_price=float(cost_price),
        stock_quantity=float(data.get('stock_quantity', 0)),
        min_stock_level=float(data.get('min_stock_level', 5)),
        uom=data.get('uom', 'pieces'),
        category_id=category_id
    )
    
    db.session.add(product)
    db.session.commit()
    RedisService.invalidate_products_cache()
    return jsonify(product.to_dict()), 201


@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json() or {}
    
    for field in ['name', 'barcode', 'description', 'price', 'cost_price', 'stock_quantity', 'min_stock_level', 'category_id', 'is_active', 'uom']:
        if field in data:
            val = data[field]
            if field == 'barcode' and (val == '' or val is None):
                val = None
            elif field == 'category_id' and (val == '' or val is None):
                val = None
            elif field == 'category_id':
                val = int(val)
            elif field in ('price', 'cost_price', 'stock_quantity', 'min_stock_level') and val is not None:
                val = float(val)
            setattr(product, field, val)
            
    db.session.commit()
    RedisService.invalidate_products_cache()
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


@product_bp.route('/events', methods=['GET'])
def events():
    def event_stream():
        # Send connection established event
        yield f"data: {json.dumps({'event': 'connected'})}\n\n"
        
        try:
            pubsub = redis_client.pubsub()
            pubsub.subscribe('pos:catalog:events')
            for message in pubsub.listen():
                if message['type'] == 'message':
                    data = message['data'].decode('utf-8') if isinstance(message['data'], bytes) else message['data']
                    yield f"data: {data}\n\n"
        except GeneratorExit:
            try:
                pubsub.unsubscribe('pos:catalog:events')
            except Exception:
                pass
        except Exception as e:
            yield f"data: {json.dumps({'event': 'heartbeat', 'error': 'Redis unavailable'})}\n\n"
            
    return Response(event_stream(), mimetype="text/event-stream")
