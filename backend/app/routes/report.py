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

@report_bp.route('/custom', methods=['GET'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def get_custom_report():
    from flask import request
    from app.models.user import User
    from app.models.store import Store
    from app.models.sale import SaleItem
    
    metric = request.args.get('metric', 'sales_per_user')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    store_id_str = request.args.get('store_id')
    cashier_id_str = request.args.get('cashier_id')
    
    # Parse dates
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
        else:
            end_date = datetime.utcnow()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
        
    store_id = int(store_id_str) if store_id_str and store_id_str != 'null' and store_id_str != '' else None
    cashier_id = int(cashier_id_str) if cashier_id_str and cashier_id_str != 'null' and cashier_id_str != '' else None
    
    data = []
    
    if metric == 'sales_per_user':
        results = db.session.query(
            User.username,
            Store.name.label('store_name'),
            func.count(Sale.id),
            func.sum(Sale.subtotal),
            func.sum(Sale.discount),
            func.sum(Sale.tax),
            func.sum(Sale.total)
        ).join(User, User.id == Sale.cashier_id)\
         .outerjoin(Store, Store.id == User.store_id)\
         .filter(Sale.created_at >= start_date, Sale.created_at <= end_date)
         
        if store_id:
            results = results.filter(User.store_id == store_id)
        if cashier_id:
            results = results.filter(Sale.cashier_id == cashier_id)
            
        results = results.group_by(User.username, Store.name).all()
        
        for username, store_name, count, subtotal, discount, tax, total in results:
            data.append({
                "cashier": username,
                "store": store_name or "Unassigned",
                "sales_count": count,
                "subtotal": float(subtotal) if subtotal else 0.00,
                "discount": float(discount) if discount else 0.00,
                "tax": float(tax) if tax else 0.00,
                "total": float(total) if total else 0.00
            })
            
    elif metric == 'day_checkouts':
        results = db.session.query(
            func.date(Sale.created_at).label('sale_date'),
            func.count(Sale.id),
            func.sum(Sale.subtotal),
            func.sum(Sale.discount),
            func.sum(Sale.tax),
            func.sum(Sale.total)
        ).filter(Sale.created_at >= start_date, Sale.created_at <= end_date)
        
        if store_id:
            results = results.join(User, User.id == Sale.cashier_id).filter(User.store_id == store_id)
        if cashier_id:
            if not store_id:
                results = results.join(User, User.id == Sale.cashier_id)
            results = results.filter(Sale.cashier_id == cashier_id)
            
        results = results.group_by(func.date(Sale.created_at))\
                         .order_by(func.date(Sale.created_at)).all()
                         
        for sale_date, count, subtotal, discount, tax, total in results:
            date_str = sale_date.isoformat() if hasattr(sale_date, 'isoformat') else str(sale_date)
            tot_val = float(total) if total else 0.00
            data.append({
                "date": date_str,
                "sales_count": count,
                "subtotal": float(subtotal) if subtotal else 0.00,
                "discount": float(discount) if discount else 0.00,
                "tax": float(tax) if tax else 0.00,
                "total": tot_val,
                "average_ticket": round(tot_val / count, 2) if count > 0 else 0.00
            })
            
    elif metric == 'shift_sales':
        from app.models.shift import Shift
        results = db.session.query(
            Shift.id,
            User.username,
            Shift.start_time,
            Shift.end_time,
            Shift.start_cash,
            Shift.end_cash,
            Shift.status,
            func.count(Sale.id),
            func.sum(Sale.total)
        ).join(User, User.id == Shift.cashier_id)\
         .outerjoin(Sale, Sale.shift_id == Shift.id)\
         .filter(Shift.start_time >= start_date, Shift.start_time <= end_date)
         
        if store_id:
            results = results.filter(User.store_id == store_id)
        if cashier_id:
            results = results.filter(Shift.cashier_id == cashier_id)
            
        results = results.group_by(
            Shift.id, User.username, Shift.start_time, Shift.end_time, 
            Shift.start_cash, Shift.end_cash, Shift.status
        ).order_by(Shift.start_time.desc()).all()
        
        for s_id, username, start, end, start_cash, end_cash, status, sales_count, total_sales in results:
            data.append({
                "shift_id": s_id[:8] if s_id else None,
                "cashier": username,
                "start_time": start.isoformat() if start else None,
                "end_time": end.isoformat() if end else None,
                "start_cash": float(start_cash),
                "end_cash": float(end_cash) if end_cash is not None else None,
                "status": status.upper(),
                "sales_count": sales_count if sales_count else 0,
                "total_sales": float(total_sales) if total_sales else 0.00
            })
            
    elif metric == 'sales_per_month':
        results = db.session.query(
            Sale.created_at,
            Sale.subtotal,
            Sale.discount,
            Sale.tax,
            Sale.total
        ).filter(Sale.created_at >= start_date, Sale.created_at <= end_date)
        
        if store_id:
            results = results.join(User, User.id == Sale.cashier_id).filter(User.store_id == store_id)
        if cashier_id:
            if not store_id:
                results = results.join(User, User.id == Sale.cashier_id)
            results = results.filter(Sale.cashier_id == cashier_id)
            
        results = results.all()
        
        from collections import defaultdict
        monthly_data = defaultdict(lambda: {
            "sales_count": 0,
            "subtotal": 0.0,
            "discount": 0.0,
            "tax": 0.0,
            "total": 0.0
        })
        
        for created_at, subtotal, discount, tax, total in results:
            month_key = created_at.strftime('%Y-%m')
            monthly_data[month_key]["sales_count"] += 1
            monthly_data[month_key]["subtotal"] += float(subtotal)
            monthly_data[month_key]["discount"] += float(discount)
            monthly_data[month_key]["tax"] += float(tax)
            monthly_data[month_key]["total"] += float(total)
            
        for month_key in sorted(monthly_data.keys()):
            m_info = monthly_data[month_key]
            data.append({
                "month": month_key,
                "sales_count": m_info["sales_count"],
                "subtotal": round(m_info["subtotal"], 2),
                "discount": round(m_info["discount"], 2),
                "tax": round(m_info["tax"], 2),
                "total": round(m_info["total"], 2),
                "average_ticket": round(m_info["total"] / m_info["sales_count"], 2) if m_info["sales_count"] > 0 else 0.00
            })
            
    elif metric == 'sales_per_store':
        results = db.session.query(
            Store.name,
            Store.code,
            func.count(Sale.id),
            func.sum(Sale.subtotal),
            func.sum(Sale.discount),
            func.sum(Sale.tax),
            func.sum(Sale.total)
        ).join(User, User.id == Sale.cashier_id)\
         .join(Store, Store.id == User.store_id)\
         .filter(Sale.created_at >= start_date, Sale.created_at <= end_date)
         
        if store_id:
            results = results.filter(Store.id == store_id)
        if cashier_id:
            results = results.filter(Sale.cashier_id == cashier_id)
            
        results = results.group_by(Store.name, Store.code).all()
        
        for store_name, store_code, count, subtotal, discount, tax, total in results:
            tot_val = float(total) if total else 0.00
            data.append({
                "store_name": store_name,
                "store_code": store_code.upper() if store_code else "",
                "sales_count": count,
                "subtotal": float(subtotal) if subtotal else 0.00,
                "discount": float(discount) if discount else 0.00,
                "tax": float(tax) if tax else 0.00,
                "total": tot_val,
                "average_ticket": round(tot_val / count, 2) if count > 0 else 0.00
            })
            
    elif metric == 'sales_by_category':
        results = db.session.query(
            Category.name,
            func.count(SaleItem.id),
            func.sum(SaleItem.quantity),
            func.sum(SaleItem.total_price)
        ).join(Product, Product.id == SaleItem.product_id)\
         .join(Category, Category.id == Product.category_id)\
         .join(Sale, Sale.id == SaleItem.sale_id)\
         .filter(Sale.created_at >= start_date, Sale.created_at <= end_date)
         
        if store_id:
            results = results.join(User, User.id == Sale.cashier_id).filter(User.store_id == store_id)
        if cashier_id:
            if not store_id:
                results = results.join(User, User.id == Sale.cashier_id)
            results = results.filter(Sale.cashier_id == cashier_id)
            
        results = results.group_by(Category.name).all()
        
        for cat_name, items_count, qty, revenue in results:
            data.append({
                "category": cat_name,
                "items_sold_count": int(items_count) if items_count else 0,
                "total_quantity": float(qty) if qty else 0.0,
                "revenue": float(revenue) if revenue else 0.00
            })
            
    return jsonify({
        "metric": metric,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "data": data
    }), 200
