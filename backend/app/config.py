import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'pos-secret-key-change-in-prod')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Databases
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'postgresql://postgres:postgres@localhost:5432/pos_db'
    )
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Token expiration
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 86400 * 7  # 7 days


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL', 
        'postgresql://postgres:postgres@localhost:5432/pos_test_db'
    )
    REDIS_URL = os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/1')


class ProductionConfig(Config):
    DEBUG = False
    # In production, require strict secrets
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
