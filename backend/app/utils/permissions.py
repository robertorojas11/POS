from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.models.user import User

def requires_user_type(*user_type_names):
    """
    Decorator to restrict access to endpoints based on the logged-in user's UserType.
    Must be placed AFTER @jwt_required() decorator.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({"error": "Authorization required"}), 401
            
            user = db.session.get(User, int(current_user_id))
            if not user:
                return jsonify({"error": "User session is invalid. Please log in again."}), 401
                
            if not user.user_type or user.user_type.name not in user_type_names:
                return jsonify({
                    "error": f"Access denied. Required user type: {', '.join(user_type_names)}"
                }), 403
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator
