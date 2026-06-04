from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import redis

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

# Redis client placeholder, will be initialized in app factory
redis_client = None

def init_redis(app):
    global redis_client
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    # decode_responses=True makes sure we get strings back from redis, not bytes
    redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
    
    # Store in app config/extensions as well for utility
    app.extensions['redis'] = redis_client
