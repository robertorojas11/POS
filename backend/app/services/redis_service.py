import json
from app import extensions

CATALOG_KEY = "pos:products:cache"
CATALOG_CHANNEL = "pos:catalog:events"


def _r():
    return extensions.redis_client


class RedisService:
    # Redis is a cache: every method fails soft so a Redis outage never blocks a sale.

    @staticmethod
    def set_cached_products(products_list):
        try:
            _r().set(CATALOG_KEY, json.dumps(products_list), ex=600)
            return True
        except Exception:
            return False

    @staticmethod
    def get_cached_products():
        try:
            data = _r().get(CATALOG_KEY)
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None

    @staticmethod
    def invalidate_products_cache(notify=True):
        """Drop the catalog cache. notify=True also nudges every till to reload (catalog edits, not sales)."""
        try:
            _r().delete(CATALOG_KEY)
            if notify:
                _r().publish(CATALOG_CHANNEL, json.dumps({"event": "invalidate"}))
        except Exception:
            pass

    @staticmethod
    def save_suspended_cart(cashier_id, cart_id, cart_data):
        try:
            _r().set(f"pos:cashier:{cashier_id}:suspended:{cart_id}", json.dumps(cart_data), ex=86400)
            return True
        except Exception:
            return False

    @staticmethod
    def get_suspended_carts(cashier_id):
        carts = {}
        try:
            for key in _r().scan_iter(f"pos:cashier:{cashier_id}:suspended:*"):
                data = _r().get(key)
                if data:
                    carts[key.split(":")[-1]] = json.loads(data)
        except Exception:
            pass
        return carts

    @staticmethod
    def delete_suspended_cart(cashier_id, cart_id):
        try:
            _r().delete(f"pos:cashier:{cashier_id}:suspended:{cart_id}")
            return True
        except Exception:
            return False

    @staticmethod
    def publish_sale_event(sale_data):
        try:
            _r().publish("pos:sales:events", json.dumps(sale_data))
            return True
        except Exception:
            return False

    # Login throttle: fail-open if Redis is down (a cache outage must not lock everyone out)
    @staticmethod
    def login_failures(key):
        try:
            return int(_r().get(f"pos:login_fail:{key}") or 0)
        except Exception:
            return 0

    @staticmethod
    def record_login_failure(key):
        try:
            k = f"pos:login_fail:{key}"
            if _r().incr(k) == 1:
                _r().expire(k, 300)
        except Exception:
            pass
