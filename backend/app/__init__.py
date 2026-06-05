from flask import Flask, jsonify
from app.config import config
from app.extensions import db, migrate, jwt, cors, init_redis

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    
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

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
        
    return app
