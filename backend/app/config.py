import os


class Config:
    # No fallback secrets here: production must set them (create_app refuses to start without).
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Access token covers a full work shift; offline tills must still sync at the end of it.
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 12 * 3600))

    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # --- Per-deployment business settings (see docs/architecture/business_profiles.md) ---
    BUSINESS_TYPE = os.getenv('BUSINESS_TYPE', 'retail')  # retail | restaurant | bar
    BUSINESS_NAME = os.getenv('BUSINESS_NAME', 'ApexPOS')
    CURRENCY = os.getenv('CURRENCY', 'USD')
    TAX_RATE = os.getenv('TAX_RATE', '0.0825')  # string: parsed to Decimal, never float
    TIMEZONE = os.getenv('TIMEZONE', 'UTC')  # store's local zone, used for "today" in reports


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-secret')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-only-jwt-secret-0123456789abcdef')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/pos_db')


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'test-secret'
    JWT_SECRET_KEY = 'test-jwt-secret-0123456789abcdef0123'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/pos_test_db'
    )
    REDIS_URL = os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/1')


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
