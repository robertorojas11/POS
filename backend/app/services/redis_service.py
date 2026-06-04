import json
from app.extensions import redis_client

class RedisService:
    @staticmethod
    def set_cached_products(products_list):
        """Cache the list of active products for rapid autocomplete search."""
        try:
            redis_client.set("pos:products:cache", json.dumps(products_list), ex=600)  # cache for 10 minutes
            return True
        except Exception:
            return False

    @staticmethod
    def get_cached_products():
        """Retrieve cached active products."""
        try:
            data = redis_client.get("pos:products:cache")
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None

    @staticmethod
    def invalidate_products_cache():
        """Delete products cache when product details or stocks change."""
        try:
            redis_client.delete("pos:products:cache")
        except Exception:
            pass

    @staticmethod
    def save_suspended_cart(cashier_id, cart_id, cart_data):
        """Suspend a transaction/cart (hold cart) to recall it later."""
        try:
            key = f"pos:cashier:{cashier_id}:suspended:{cart_id}"
            redis_client.set(key, json.dumps(cart_data), ex=86400)  # expires in 24 hours
            return True
        except Exception:
            return False

    @staticmethod
    def get_suspended_carts(cashier_id):
        """Retrieve all suspended carts for a cashier."""
        carts = {}
        try:
            pattern = f"pos:cashier:{cashier_id}:suspended:*"
            keys = redis_client.keys(pattern)
            for key in keys:
                cart_id = key.split(":")[-1]
                data = redis_client.get(key)
                if data:
                    carts[cart_id] = json.loads(data)
        except Exception:
            pass
        return carts

    @staticmethod
    def delete_suspended_cart(cashier_id, cart_id):
        """Delete a suspended cart after it has been retrieved/resumed."""
        try:
            key = f"pos:cashier:{cashier_id}:suspended:{cart_id}"
            redis_client.delete(key)
            return True
        except Exception:
            return False

    @staticmethod
    def publish_sale_event(sale_data):
        """Publish a completed sale event for real-time integrations (e.g. screens or receipt printers)."""
        try:
            redis_client.publish("pos:sales:events", json.dumps(sale_data))
            return True
        except Exception:
            return False
