from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app.extensions import db
from app.models import Sale, Discount, Customer, Shift
from app.services.sales_service import SalesService
from app.services.redis_service import RedisService
from app.utils.permissions import requires_user_type

sale_bp = Blueprint('sale', __name__)

@sale_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    cart_items = data.get('items', [])
    payment_method = data.get('payment_method', 'cash')
    payment_details = data.get('payment_details')
    customer_id = data.get('customer_id')
    discount = data.get('discount', 0.00)
    tax_rate = data.get('tax_rate', 0.0825)
    
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400
        
    try:
        sale_result = SalesService.process_checkout(
            cashier_id=current_user_id,
            cart_items=cart_items,
            payment_method=payment_method,
            customer_id=customer_id,
            discount=discount,
            tax_rate=tax_rate,
            payment_details=payment_details
        )
        return jsonify({
            "message": "Checkout completed successfully",
            "sale": sale_result
        }), 201
    except ValueError as val_err:
        return jsonify({"error": str(val_err)}), 400
    except Exception as exc:
        return jsonify({"error": f"Checkout failed: {str(exc)}"}), 500


@sale_bp.route('/history', methods=['GET'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def sale_history():
    # Fetch recent sales transactions
    limit = min(int(request.args.get('limit', 50)), 100)
    sales = Sale.query.order_by(Sale.created_at.desc()).limit(limit).all()
    return jsonify([sale.to_dict() for sale in sales]), 200


@sale_bp.route('/invoice/<string:invoice_num>', methods=['GET'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def get_invoice(invoice_num):
    sale = Sale.query.filter_by(invoice_number=invoice_num).first_or_404()
    return jsonify(sale.to_dict()), 200


@sale_bp.route('/suspend', methods=['POST'])
@jwt_required()
def suspend_cart():
    current_cashier_id = get_jwt_identity()
    data = request.get_json() or {}
    
    cart_id = data.get('cart_id')
    cart_data = data.get('cart_data')
    
    if not cart_id or not cart_data:
        return jsonify({"error": "Cart ID and Cart Data required"}), 400
        
    success = RedisService.save_suspended_cart(current_cashier_id, cart_id, cart_data)
    if success:
        return jsonify({"message": "Cart suspended successfully", "cart_id": cart_id}), 200
    return jsonify({"error": "Could not suspend cart in cache"}), 500


@sale_bp.route('/suspend', methods=['GET'])
@jwt_required()
def get_suspended():
    current_cashier_id = get_jwt_identity()
    carts = RedisService.get_suspended_carts(current_cashier_id)
    return jsonify(carts), 200


@sale_bp.route('/suspend/<string:cart_id>', methods=['DELETE'])
@jwt_required()
def delete_suspended(cart_id):
    current_cashier_id = get_jwt_identity()
    success = RedisService.delete_suspended_cart(current_cashier_id, cart_id)
    if success:
        return jsonify({"message": "Suspended cart deleted successfully"}), 200
    return jsonify({"error": "Could not delete suspended cart from cache"}), 500


# Customer-related convenience route nested under sales
@sale_bp.route('/customers', methods=['GET', 'POST'])
@jwt_required()
def handle_customers():
    if request.method == 'GET':
        phone = request.args.get('phone', '')
        if phone:
            customer = Customer.query.filter_by(phone=phone).first()
            return jsonify(customer.to_dict() if customer else {}), 200
        customers = Customer.query.all()
        return jsonify([c.to_dict() for c in customers]), 200
        
    elif request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        
        if not name or not phone:
            return jsonify({"error": "Name and Phone are required"}), 400
            
        if Customer.query.filter_by(phone=phone).first():
            return jsonify({"error": "Customer with this phone already exists"}), 400
            
        customer = Customer(name=name, phone=phone, email=email)
        db.session.add(customer)
        db.session.commit()
        return jsonify(customer.to_dict()), 201


@sale_bp.route('/discounts', methods=['GET'])
@jwt_required()
def get_discounts():
    discounts = Discount.query.all()
    return jsonify([d.to_dict() for d in discounts]), 200


@sale_bp.route('/discounts/validate/<code>', methods=['GET'])
@jwt_required()
def validate_discount(code):
    code_cleaned = str(code).strip().upper()
    discount = Discount.query.filter_by(code=code_cleaned, is_active=True).first()
    if not discount:
        return jsonify({"error": "Invalid or inactive discount code"}), 404
    return jsonify(discount.to_dict()), 200



@sale_bp.route('/discounts', methods=['POST'])
@jwt_required()
@requires_user_type('Admin')
def create_discount():
    data = request.get_json() or {}
    code = str(data.get('code', '')).strip().upper()
    value = data.get('value')
    discount_type = data.get('discount_type', 'fixed')
    
    if not code or value is None:
        return jsonify({"error": "Discount code and value required"}), 400
        
    try:
        val_num = float(value)
        if val_num < 0:
            return jsonify({"error": "Discount value must be a positive number"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Discount value must be a valid number"}), 400
        
    if discount_type not in ('fixed', 'percent'):
        return jsonify({"error": "Discount type must be either 'fixed' or 'percent'"}), 400
        
    if discount_type == 'percent' and val_num > 100:
        return jsonify({"error": "Percentage discount cannot exceed 100%"}), 400
        
    if Discount.query.filter_by(code=code).first():
        return jsonify({"error": "Discount code already exists"}), 400
        
    discount = Discount(code=code, value=val_num, discount_type=discount_type)
    db.session.add(discount)
    db.session.commit()
    return jsonify(discount.to_dict()), 201


@sale_bp.route('/shifts/start', methods=['POST'])
@jwt_required()
def start_shift():
    current_cashier_id = int(get_jwt_identity())
    data = request.get_json() or {}
    start_cash = data.get('start_cash')
    
    if start_cash is None:
        return jsonify({"error": "Starting cash is required"}), 400
        
    try:
        start_cash_val = float(start_cash)
        if start_cash_val < 0:
            return jsonify({"error": "Starting cash cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Starting cash must be a valid number"}), 400
        
    # Check if there is an active shift
    active_shift = Shift.query.filter_by(cashier_id=current_cashier_id, status='open').first()
    if active_shift:
        return jsonify({"error": "You already have an active open shift session"}), 400
        
    shift = Shift(cashier_id=current_cashier_id, start_cash=start_cash_val, status='open', created_by_id=current_cashier_id)
    db.session.add(shift)
    db.session.commit()
    
    return jsonify(shift.to_dict()), 201


@sale_bp.route('/shifts/close', methods=['POST'])
@jwt_required()
def close_shift():
    current_cashier_id = int(get_jwt_identity())
    data = request.get_json() or {}
    actual_cash = data.get('actual_cash')
    
    if actual_cash is None:
        return jsonify({"error": "Actual cash in drawer is required to close shift"}), 400
        
    try:
        actual_cash_val = float(actual_cash)
        if actual_cash_val < 0:
            return jsonify({"error": "Actual cash in drawer cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Actual cash in drawer must be a valid number"}), 400
        
    active_shift = Shift.query.filter_by(cashier_id=current_cashier_id, status='open').first()
    if not active_shift:
        return jsonify({"error": "No active open shift session found to close"}), 400
        
    # Calculate cash sales during this shift
    cash_sales_query = db.session.query(func.sum(Sale.cash_amount)).filter(
        Sale.shift_id == active_shift.id
    ).scalar()
    total_cash_sales = float(cash_sales_query) if cash_sales_query else 0.00
    
    # Calculate expected cash: opening cash + cash sales
    expected_cash = float(active_shift.start_cash) + total_cash_sales
    variance = actual_cash_val - expected_cash
    
    # Calculate sales by other payment methods
    card_sales_query = db.session.query(func.sum(Sale.card_amount)).filter(
        Sale.shift_id == active_shift.id
    ).scalar()
    total_card_sales = float(card_sales_query) if card_sales_query else 0.00
    
    mobile_sales_query = db.session.query(func.sum(Sale.mobile_amount)).filter(
        Sale.shift_id == active_shift.id
    ).scalar()
    total_mobile_sales = float(mobile_sales_query) if mobile_sales_query else 0.00
    
    # Close the shift session
    active_shift.status = 'closed'
    active_shift.end_time = datetime.utcnow()
    active_shift.end_cash = actual_cash_val
    active_shift.updated_by_id = current_cashier_id
    
    db.session.commit()
    
    return jsonify({
        "message": "Shift turn closed successfully",
        "report": {
            "shift_id": active_shift.id,
            "cashier_id": active_shift.cashier_id,
            "cashier_name": active_shift.cashier.username if active_shift.cashier else 'Unknown',
            "start_time": active_shift.start_time.isoformat(),
            "end_time": active_shift.end_time.isoformat(),
            "start_cash": float(active_shift.start_cash),
            "total_cash_sales": total_cash_sales,
            "expected_cash": expected_cash,
            "actual_cash": float(actual_cash),
            "variance": round(variance, 2),
            "other_sales": {
                "card": total_card_sales,
                "mobile_pay": total_mobile_sales
            },
            "status": "closed"
        }
    }), 200


@sale_bp.route('/shifts/active', methods=['GET'])
@jwt_required()
def active_shift():
    current_cashier_id = int(get_jwt_identity())
    shift = Shift.query.filter_by(cashier_id=current_cashier_id, status='open').first()
    if not shift:
        return jsonify({"active": False, "shift": None}), 200
        
    # Calculate current expected cash on the fly
    cash_sales_query = db.session.query(func.sum(Sale.cash_amount)).filter(
        Sale.shift_id == shift.id
    ).scalar()
    total_cash_sales = float(cash_sales_query) if cash_sales_query else 0.00
    
    expected_cash = float(shift.start_cash) + total_cash_sales
    
    shift_dict = shift.to_dict()
    shift_dict['expected_cash'] = expected_cash
    shift_dict['current_cash_sales'] = total_cash_sales
    
    return jsonify({"active": True, "shift": shift_dict}), 200


@sale_bp.route('/shifts/history', methods=['GET'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def shift_history():
    shifts = Shift.query.order_by(Shift.start_time.desc()).all()
    return jsonify([s.to_dict() for s in shifts]), 200


@sale_bp.route('/shifts/active-all', methods=['GET'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def active_shifts_all():
    active_shifts = Shift.query.filter_by(status='open').all()
    
    results = []
    for s in active_shifts:
        cash_sales_query = db.session.query(func.sum(Sale.cash_amount)).filter(
            Sale.shift_id == s.id
        ).scalar()
        total_cash_sales = float(cash_sales_query) if cash_sales_query else 0.00
        
        expected_cash = float(s.start_cash) + total_cash_sales
        
        shift_data = s.to_dict()
        shift_data['expected_cash'] = expected_cash
        shift_data['current_cash_sales'] = total_cash_sales
        results.append(shift_data)
        
    return jsonify(results), 200

