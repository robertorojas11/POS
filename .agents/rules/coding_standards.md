# Codebase Rules & Coding Standards

This document establishes development guidelines for the ApexPOS project. AI agents and developers must follow these principles.

---

## 1. Backend Architecture (Flask)
- **Application Factory**: Always instantiate the Flask app using the `create_app()` factory in `app/__init__.py`. Do not initialize global variables on import.
- **ORM & Models**: Use SQLAlchemy via Flask-SQLAlchemy. Always verify that new model classes are imported in `app/models/__init__.py` so that Flask-Migrate registers them properly.
- **Atomic Checkout Transactions**: When writing controllers that touch inventory stock quantities, wrap them in a secure transactional block with database locks (`with_for_update()`) to prevent race conditions during concurrent POS sales checkout.
- **Service Layer**: Extract complex multi-step business logic (checkout, cache management) into service classes in `app/services/`. Simple CRUD remains in route handlers.
- **Permissions**: Use the `@requires_user_type()` decorator from `app/utils/permissions.py` for role-based access control. Place it AFTER `@jwt_required()`.

## 2. Frontend Architecture (Vue 3)
- **State Management**: Use Pinia stores for global application states (e.g. `auth.js`, `cart.js`, `products.js`). Do not keep transactional states in local Vue page components.
- **Components**: Reusable dashboard components go under `src/components/`, while page routers load target files under `src/views/`.
- **API Proxy**: Always write API requests with relative URLs (e.g. `/api/auth/login`). Vite is pre-configured with a proxy target to reroute these to the Flask backend dev server.
- **Aesthetic Guidelines**: Use the design system defined in `src/style.css` — CSS variables for colors, radii, shadows, and transitions. Use the `Outfit` font family. Use `lucide-vue-next` for icons.
- **SFC Standards**: Always use `<script setup>` and `<style scoped>`. Define props with types and defaults via `defineProps()`.

## 3. Databases (Postgres & Redis)
- **PostgreSQL**: Serves as the primary source of truth for transactions, inventory logs, user roles, and loyalty customers.
- **Redis**: Serves as the transient caching layer for suspended checkouts and active catalog caches. If any product is updated, ensure `RedisService.invalidate_products_cache()` is called.
- **Audit Trail**: Every table must include `created_at`, `updated_at`, `created_by_id`, and `updated_by_id` columns.

## 4. Naming Conventions
| Artifact | Convention | Example |
|----------|-----------|--------|
| Python models | PascalCase class, snake_case table | `Product` → `products` |
| Python routes | Blueprint with `_bp` suffix | `product_bp`, `sale_bp` |
| Python services | `<Domain>Service` class | `SalesService`, `RedisService` |
| Vue views | PascalCase + `View` suffix | `ProductsView.vue` |
| Vue components | PascalCase | `ProductCard.vue` |
| Pinia stores | camelCase file, `use<Name>Store` | `products.js` → `useProductsStore` |
| CSS variables | `--category-descriptor` | `--bg-card`, `--accent-lime` |
| CSS classes | kebab-case with `pos-` prefix | `.pos-btn-accent` |
| API endpoints | `/api/<resource>` RESTful | `/api/products`, `/api/sales/checkout` |
| Redis keys | `pos:<domain>:<action>:<id>` | `pos:products:cache:terminal_A` |
| DB columns | snake_case | `stock_quantity`, `created_by_id` |

## 5. Additional Rules References
Detailed rules are maintained in companion documents:
- [Architecture Rules](file:///D:/ERP/POS/.agents/rules/architecture.md)
- [Backend Conventions](file:///D:/ERP/POS/.agents/rules/backend_conventions.md)
- [Frontend Conventions](file:///D:/ERP/POS/.agents/rules/frontend_conventions.md)
- [API Contract Rules](file:///D:/ERP/POS/.agents/rules/api_contracts.md)
- [Database Standards](file:///D:/ERP/POS/.agents/rules/database_standards.md)
