from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.utils.permissions import requires_user_type
from sqlalchemy import func
from datetime import datetime, date, timedelta
from app.extensions import db
from app.models.sale import Sale, SaleItem
from app.models.product import Product, Category

report_bp = Blueprint('report', __name__)

@report_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def dashboard_stats():
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    
    # Total sales revenue today
    today_sales_query = db.session.query(func.sum(Sale.total)).filter(Sale.created_at >= start_of_day).scalar()
    today_sales_revenue = float(today_sales_query) if today_sales_query else 0.00
    
    # Total transactions today
    today_transactions_count = Sale.query.filter(Sale.created_at >= start_of_day).count()
    
    # Average transaction size today
    avg_transaction_size = today_sales_revenue / today_transactions_count if today_transactions_count > 0 else 0.00
    
    # Low stock items count
    low_stock_count = Product.query.filter(Product.stock_quantity <= Product.min_stock_level, Product.is_active == True).count()
    
    return jsonify({
        "today_revenue": today_sales_revenue,
        "today_transactions": today_transactions_count,
        "average_ticket": round(avg_transaction_size, 2),
        "low_stock_alerts": low_stock_count
    }), 200


@report_bp.route('/low-stock', methods=['GET'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def low_stock_items():
    low_stock_products = Product.query.filter(
        Product.stock_quantity <= Product.min_stock_level, 
        Product.is_active == True
    ).all()
    return jsonify([p.to_dict() for p in low_stock_products]), 200


@report_bp.route('/sales-by-category', methods=['GET'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def sales_by_category():
    # Group sale items by product -> category and sum totals
    results = db.session.query(
        Category.name, 
        func.sum(SaleItem.total_price),
        func.sum(SaleItem.quantity)
    ).join(Product, Product.id == SaleItem.product_id)\
     .join(Category, Category.id == Product.category_id)\
     .group_by(Category.name).all()
     
    sales_data = []
    for cat_name, total_revenue, total_qty in results:
        sales_data.append({
            "category": cat_name,
            "revenue": float(total_revenue) if total_revenue else 0.00,
            "items_sold": int(total_qty) if total_qty else 0
        })
        
    return jsonify(sales_data), 200
