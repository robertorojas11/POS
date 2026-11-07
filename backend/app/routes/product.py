from flask import Blueprint, jsonify, request, Response
import json
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from app import extensions
from app.models.product import Product, Category
from app.extensions import db
from app.utils.permissions import requires_user_type
from app.services.redis_service import RedisService, CATALOG_CHANNEL
from app.utils.validation import to_decimal

product_bp = Blueprint('product', __name__)

@product_bp.route('', methods=['GET'])
@jwt_required()
def get_products():
    search = request.args.get('search', '')
    category_id = request.args.get('category_id')
    barcode = request.args.get('barcode', '')
    is_full_catalog = not any([search, category_id, barcode])
    if is_full_catalog:
        cached = RedisService.get_cached_products()
        if cached:
            return jsonify(cached), 200
            
    query = Product.query.filter(Product.is_active == True)
    
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) | 
            (Product.sku.ilike(f'%{search}%'))
        )
    if category_id:
        query = query.filter(Product.category_id == request.args.get('category_id', type=int))
    if barcode:
        query = query.filter(Product.barcode == barcode)
        
    products = query.all()
    products_list = [p.to_dict() for p in products]
    
    if is_full_catalog:
        RedisService.set_cached_products(products_list)
        
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


def _clean_product_fields(data, partial):
    """Validate and convert product input once. Raises ValueError -> 400. Returns only the fields present."""
    out = {}
    for field in ('price', 'cost_price', 'stock_quantity', 'min_stock_level'):
        if field in data:
            out[field] = to_decimal(data[field], field)
    if 'min_sale_qty' in data:
        out['min_sale_qty'] = to_decimal(data['min_sale_qty'], 'min_sale_qty', allow_zero=False)
    if 'category_id' in data:
        cid = data['category_id']
        out['category_id'] = None if cid in ('', None) else int(cid)
    if 'barcode' in data:
        out['barcode'] = data['barcode'] or None
    if 'is_active' in data:
        out['is_active'] = bool(data['is_active'])
    for field in ('name', 'description', 'uom'):
        if field in data:
            if field in ('name', 'uom') and not str(data[field] or '').strip():
                raise ValueError(f"{field} cannot be empty")
            out[field] = data[field]
    if not partial:
        for field in ('sku', 'name', 'price', 'cost_price'):
            if field not in data or data[field] in (None, ''):
                raise ValueError("SKU, Name, Price, and Cost Price are required")
        out['sku'] = data['sku']
    return out


@product_bp.route('', methods=['POST'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def create_product():
    data = request.get_json() or {}
    try:
        fields = _clean_product_fields(data, partial=False)
    except (ValueError, TypeError) as err:
        return jsonify({"error": str(err)}), 400

    if Product.query.filter_by(sku=fields['sku']).first():
        return jsonify({"error": "Product with this SKU already exists"}), 400
    if fields.get('barcode') and Product.query.filter_by(barcode=fields['barcode']).first():
        return jsonify({"error": f"Product with barcode '{fields['barcode']}' already exists"}), 400

    product = Product(created_by_id=int(get_jwt_identity()), **fields)
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
    data.pop('sku', None)  # SKU is immutable after creation
    try:
        fields = _clean_product_fields(data, partial=True)
    except (ValueError, TypeError) as err:
        return jsonify({"error": str(err)}), 400

    barcode = fields.get('barcode')
    if barcode and Product.query.filter(Product.barcode == barcode, Product.id != product_id).first():
        return jsonify({"error": f"Product with barcode '{barcode}' already exists"}), 400

    for field, value in fields.items():
        setattr(product, field, value)
    product.updated_by_id = int(get_jwt_identity())
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
    # EventSource cannot send an Authorization header, so the token comes in the query string
    try:
        decode_token(request.args.get('token', ''))
    except Exception:
        return jsonify({"error": "Authorization required"}), 401

    def event_stream():
        yield f"data: {json.dumps({'event': 'connected'})}\n\n"
        pubsub = None
        try:
            pubsub = extensions.redis_client.pubsub()
            pubsub.subscribe(CATALOG_CHANNEL)
            while True:
                # Timeout turns into a keepalive; a dead client raises GeneratorExit on the write
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=15)
                yield f"data: {message['data']}\n\n" if message else ": keepalive\n\n"
        except GeneratorExit:
            raise
        except Exception:
            yield f"data: {json.dumps({'event': 'heartbeat', 'error': 'Redis unavailable'})}\n\n"
        finally:
            if pubsub:
                try:
                    pubsub.close()
                except Exception:
                    pass

    return Response(event_stream(), mimetype="text/event-stream")
