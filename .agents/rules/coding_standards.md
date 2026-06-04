# Codebase Rules & Coding Standards

This document establishes development guidelines for the ApexPOS project. AI agents and developers must follow these principles.

---

## 1. Backend Architecture (Flask)
- **Application Factory**: Always instantiate the Flask app using the `create_app()` factory in `app/__init__.py`. Do not initialize global variables on import.
- **ORM & Models**: Use SQLAlchemy via Flask-SQLAlchemy. Always verify that new model classes are imported in `app/models/__init__.py` so that Flask-Migrate registers them properly.
- **Atomic Checkout Transactions**: When writing controllers that touch inventory stock quantities, wrap them in a secure transactional block with database locks (`with_for_update()`) to prevent race conditions during concurrent POS sales checkout.

## 2. Frontend Architecture (Vue 3)
- **State Management**: Use Pinia stores for global application states (e.g. `auth.js`, `cart.js`, `products.js`). Do not keep transactional states in local Vue page components.
- **Components**: Reusable dashboard components go under `src/components/`, while page routers load target files under `src/views/`.
- **API Proxy**: Always write API requests with relative URLs (e.g. `/api/auth/login`). Vite is pre-configured with a proxy target to reroute these to the Flask backend dev server.
- **Aesthetic Guidelines**: Keep layouts responsive, use slate dark mode classes from `src/style.css`, and use smooth SVG animations or custom CSS transition states to give a premium feel.

## 3. Databases (Postgres & Redis)
- **PostgreSQL**: Serves as the primary source of truth for transactions, inventory logs, user roles, and loyalty customers.
- **Redis**: Serves as the transient caching layer for suspended checkouts and active catalog caches. If any product is updated, ensure `RedisService.invalidate_products_cache()` is called.
