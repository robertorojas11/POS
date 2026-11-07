from decimal import Decimal
from flask import Flask, jsonify
from app.config import config
from app.business import features_for
from app.extensions import db, migrate, jwt, cors, init_redis

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])

    if not app.config.get('SECRET_KEY') or not app.config.get('JWT_SECRET_KEY'):
        raise RuntimeError("SECRET_KEY and JWT_SECRET_KEY must be set")
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise RuntimeError("DATABASE_URL must be set")
    app.config['TAX_RATE'] = Decimal(str(app.config['TAX_RATE']))  # fails fast on a bad value
    features = features_for(app.config['BUSINESS_TYPE'])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    origins = app.config['CORS_ORIGINS']
    cors.init_app(app, resources={r"/api/*": {"origins": origins if origins == '*' else origins.split(',')}})

    # Reject tokens of deleted or deactivated users on every protected route
    @jwt.token_in_blocklist_loader
    def user_is_gone(jwt_header, jwt_payload):
        from app.models.user import User
        user = db.session.get(User, int(jwt_payload['sub']))
        return user is None or not user.is_active

    
    # Initialize Redis
    init_redis(app)
    
    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.product import product_bp
    from app.routes.sale import sale_bp
    from app.routes.report import report_bp
    from app.routes.store import store_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(sale_bp, url_prefix='/api/sales')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(store_bp, url_prefix='/api/stores')
    
    # Simple Health Check Route
    @app.route('/health')
    def health_check():
        # Quick ping to db and redis to confirm connectivity
        status = {"status": "healthy", "services": {"database": "unknown", "redis": "unknown"}}
        try:
            db.session.execute(db.text("SELECT 1"))
            status["services"]["database"] = "up"
        except Exception as e:
            status["status"] = "unhealthy"
            status["services"]["database"] = f"down: {str(e)}"
            
        try:
            from app.extensions import redis_client
            redis_client.ping()
            status["services"]["redis"] = "up"
        except Exception as e:
            status["status"] = "unhealthy"
            status["services"]["redis"] = f"down: {str(e)}"
            
        code = 200 if status["status"] == "healthy" else 500
        return jsonify(status), code

    @app.route('/api/config')
    def business_config():
        # Public on purpose: the login screen needs it. No secrets here.
        return jsonify({
            "business_name": app.config['BUSINESS_NAME'],
            "business_type": app.config['BUSINESS_TYPE'],
            "currency": app.config['CURRENCY'],
            "tax_rate": float(app.config['TAX_RATE']),
            "features": features,
        }), 200

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
        
    return app
