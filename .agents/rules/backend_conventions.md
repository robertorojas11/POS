# Backend Conventions

Rules governing Flask backend development in ApexPOS.

---

## 1. Application Factory
- Always use `create_app(config_name)` from `app/__init__.py`.
- Never instantiate Flask directly outside the factory.
- All blueprint registration happens inside `create_app()`.
- Import blueprints lazily inside the factory function to avoid circular imports.

## 2. Model Standards
- Every model MUST define `__tablename__` (plural snake_case).
- Every model MUST include these audit columns:
  - `created_at` — `db.DateTime, default=datetime.utcnow`
  - `updated_at` — `db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow`
  - `created_by_id` — `db.Integer, db.ForeignKey('users.id')`
  - `updated_by_id` — `db.Integer, db.ForeignKey('users.id')`
- Every model MUST have a `to_dict()` method returning a plain Python dict.
- Every model MUST be imported in `app/models/__init__.py` and listed in `__all__`.
- Use `db.Numeric(10, 2)` for money, `db.Numeric(10, 3)` for quantities.
- Prefer `back_populates` over `backref` for relationships.

## 3. Route/Controller Standards
- Blueprint variable: `<entity>_bp = Blueprint('<entity>', __name__)`.
- All endpoints MUST have `@jwt_required()` (except login, register, health, SSE).
- `@requires_user_type(...)` MUST be placed AFTER `@jwt_required()`.
- Input parsing: `data = request.get_json() or {}`.
- Set `created_by_id = int(get_jwt_identity())` on all create operations.
- Set `updated_by_id = int(get_jwt_identity())` on all update operations.

## 4. Service Layer Standards
- Services are classes with `@staticmethod` methods.
- Service class naming: `<Domain>Service` (e.g., `SalesService`, `RedisService`).
- Services are for complex multi-step operations (checkout, cache management).
- Simple CRUD does NOT require a service — handle directly in routes.

## 5. Error Handling
- Return `{"error": "descriptive message"}` with appropriate HTTP status.
- Catch `ValueError` for validation errors → 400.
- Use `try/except` with `db.session.rollback()` for transactional operations.
- Never expose stack traces or internal details in error messages.

## 6. Redis Conventions
- Key namespace: `pos:<domain>:<action>:<identifier>` (colon-separated).
- Always call `RedisService.invalidate_products_cache()` after product-related mutations.
- All Redis operations MUST be wrapped in try/except (Redis may be unavailable).

## 7. Testing Standards
- Test files: `backend/tests/test_<domain>.py`.
- Use `create_app('testing')` with `TestingConfig`.
- Seed UserTypes (1=Admin, 2=Manager, 3=Operator) in every setUp.
- Authenticate and store headers in `self.headers` for reuse.
- Clean tables in FK-dependency order in setUp.
