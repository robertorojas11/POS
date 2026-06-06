---
name: creating-api-endpoints
description: Creates new Flask Blueprint API endpoints for the ApexPOS backend. Use when adding new REST routes, controllers, or API functionality.
---

# Creating API Endpoints

## When to use this skill
- Adding a new REST resource to the ApexPOS API.
- Extending an existing blueprint with new endpoints.
- Creating a new feature that requires backend routes.

## Workflow
1. [ ] **Determine blueprint**: Decide if the endpoint belongs to an existing blueprint or requires a new one.
2. [ ] **Create/update route file** in `backend/app/routes/`.
3. [ ] **Register blueprint** in `backend/app/__init__.py` (if new).
4. [ ] **Add permission decorators** as needed.
5. [ ] **Test** using the `running-backend-tests` skill.

## Instructions

### 1. Blueprint File Structure
Every route file follows this structure:

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import YourModel
from app.utils.permissions import requires_user_type

your_bp = Blueprint('your_resource', __name__)

@your_bp.route('', methods=['GET'])
@jwt_required()
def get_items():
    items = YourModel.query.all()
    return jsonify([item.to_dict() for item in items]), 200

@your_bp.route('/<int:item_id>', methods=['GET'])
@jwt_required()
def get_item(item_id):
    item = YourModel.query.get_or_404(item_id)
    return jsonify(item.to_dict()), 200

@your_bp.route('', methods=['POST'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def create_item():
    data = request.get_json() or {}
    # Validate required fields
    name = data.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400
    # Check uniqueness
    if YourModel.query.filter_by(name=name).first():
        return jsonify({"error": "Item already exists"}), 400
    # Create
    item = YourModel(
        name=name,
        created_by_id=int(get_jwt_identity())
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@your_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
@requires_user_type('Admin', 'Manager')
def update_item(item_id):
    item = YourModel.query.get_or_404(item_id)
    data = request.get_json() or {}
    for field in ['name', 'description', 'is_active']:
        if field in data:
            setattr(item, field, data[field])
    item.updated_by_id = int(get_jwt_identity())
    db.session.commit()
    return jsonify(item.to_dict()), 200

@your_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
@requires_user_type('Admin')
def delete_item(item_id):
    item = YourModel.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted successfully"}), 200
```

### 2. Response Format Conventions
| Scenario | Response Body | Status |
|----------|--------------|--------|
| Success (single entity) | `entity.to_dict()` | 200 |
| Success (list) | `[e.to_dict() for e in entities]` | 200 |
| Created | `entity.to_dict()` | 201 |
| Validation error | `{"error": "descriptive message"}` | 400 |
| Unauthorized | `{"error": "Authorization required"}` | 401 |
| Forbidden | `{"error": "Access denied. Required user type: ..."}` | 403 |
| Not found | `{"error": "Resource not found"}` | 404 |
| Server error | `{"error": "descriptive message"}` | 500 |
| Action success (no entity) | `{"message": "Action completed"}` | 200 |

### 3. Authentication & Authorization
- **All endpoints** (except health, login, register, SSE) require `@jwt_required()`.
- Place `@requires_user_type(...)` **AFTER** `@jwt_required()`.
- Get current user ID: `current_user_id = int(get_jwt_identity())`.
- Role hierarchy: `Admin` > `Manager` > `Operator`.

### 4. Input Validation Pattern
```python
data = request.get_json() or {}  # Always fallback to empty dict
field = data.get('field_name')
if not field:
    return jsonify({"error": "Field name is required"}), 400
```

### 5. Cache Invalidation
If the endpoint modifies product-related data:
```python
from app.services.redis_service import RedisService
RedisService.invalidate_products_cache()
```

### 6. Blueprint Registration
For new blueprints, add to `backend/app/__init__.py`:
```python
from app.routes.your_resource import your_bp
app.register_blueprint(your_bp, url_prefix='/api/your-resource')
```

### 7. Existing Blueprints
| Blueprint | File | Prefix | Domain |
|-----------|------|--------|--------|
| `auth_bp` | `auth.py` | `/api/auth` | Users, employees, login |
| `product_bp` | `product.py` | `/api/products` | Products, categories, SSE |
| `sale_bp` | `sale.py` | `/api/sales` | Checkout, shifts, discounts, suspend |
| `report_bp` | `report.py` | `/api/reports` | Dashboard, custom reports |
| `store_bp` | `store.py` | `/api/stores` | Store/sucursal management |

## Why This Skill Exists
- **Protects**: Consistent error format, auth enforcement, response structure.
- **Prevents**: Endpoints without JWT, inconsistent error messages, missing audit fields on writes.
- **Evolution**: Consider adding request schema validation (marshmallow/pydantic) as endpoints grow.
