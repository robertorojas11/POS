---
name: creating-backend-models
description: Creates new SQLAlchemy models for the ApexPOS Flask backend. Use when adding a new database entity, table, or domain model to the system.
---

# Creating Backend Models

## When to use this skill
- Adding a new database table/entity to ApexPOS.
- Extending the data model with a new domain concept.
- Adding fields or relationships to existing models.

## Workflow
1. [ ] **Identify domain entity** and determine its table name, columns, and relationships.
2. [ ] **Create model file** in `backend/app/models/` following the established pattern.
3. [ ] **Register model** in `backend/app/models/__init__.py`.
4. [ ] **Generate migration** using the `db-migration` skill.
5. [ ] **Verify** the model is correctly picked up by Flask-Migrate.

## Instructions

### 1. File Naming
- One file per domain entity (or closely related pair, e.g., `sale.py` contains `Sale`, `SaleItem`, `Discount`).
- Filename: **singular snake_case** matching the primary model (e.g., `product.py`, `customer.py`, `shift.py`).

### 2. Model Template
Every model MUST include the full set of audit fields and a `to_dict()` serializer:

```python
from datetime import datetime
from app.extensions import db

class NewEntity(db.Model):
    __tablename__ = 'new_entities'  # plural snake_case
    
    id = db.Column(db.Integer, primary_key=True)
    # --- Domain-specific columns ---
    name = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # --- Audit columns (REQUIRED on every model) ---
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # --- Relationships ---
    creator = db.relationship('User', foreign_keys=[created_by_id])
    updater = db.relationship('User', foreign_keys=[updated_by_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by_id': self.created_by_id,
            'updated_by_id': self.updated_by_id
        }
```

### 3. Column Type Conventions
| Data Type | SQLAlchemy Type | Example |
|-----------|----------------|---------|
| Money/currency | `db.Numeric(10, 2)` | `price`, `total`, `start_cash` |
| Quantities (weighted) | `db.Numeric(10, 3)` | `stock_quantity`, `min_sale_qty` |
| Short text | `db.String(N)` | `name` (128), `sku` (64), `code` (32) |
| Long text | `db.Text` | `description`, `notes` |
| Status/enum | `db.String(16-32)` | `status` (open/closed), `payment_method` |
| Boolean flags | `db.Boolean` | `is_active`, `must_change_password` |
| UUID primary keys | `db.String(36)` + lambda default | Only for `Shift` model; all others use Integer |

### 4. Relationship Patterns
- Use `back_populates` (not `backref`) as the primary pattern.
- For self-referential FKs (e.g., `created_by_id` on User), add `remote_side=[id]`.
- For circular FK dependencies, use `use_alter=True` and explicit `name` on the ForeignKey.
- Lazy loading: `lazy='dynamic'` for large collections, `lazy='subquery'` for always-needed children (e.g., SaleItems).

### 5. Registration in __init__.py
After creating the model file, add the import and `__all__` entry:

```python
# In backend/app/models/__init__.py
from app.models.new_entity import NewEntity

__all__ = [
    # ... existing models ...
    'NewEntity'
]
```

> **CRITICAL**: If you skip this step, Flask-Migrate will NOT detect the new model and no migration will be generated.

### 6. Existing Models Reference
| Model | File | Table | PK Type |
|-------|------|-------|---------|
| `User` | `user.py` | `users` | Integer |
| `UserType` | `user.py` | `user_types` | Integer |
| `Category` | `product.py` | `categories` | Integer |
| `Product` | `product.py` | `products` | Integer |
| `Sale` | `sale.py` | `sales` | Integer |
| `SaleItem` | `sale.py` | `sale_items` | Integer |
| `Discount` | `sale.py` | `discounts` | Integer |
| `Customer` | `customer.py` | `customers` | Integer |
| `Shift` | `shift.py` | `shifts` | UUID String(36) |
| `Store` | `store.py` | `stores` | Integer |
| `InventoryLog` | `inventory.py` | `inventory_logs` | Integer |

## Why This Skill Exists
- **Protects**: Consistent audit trail across all entities, uniform serialization via `to_dict()`.
- **Prevents**: Models missing audit fields, forgotten `__init__.py` registration, inconsistent column types.
- **Evolution**: As the project grows, consider extracting audit fields into a `TimestampMixin` base class.
