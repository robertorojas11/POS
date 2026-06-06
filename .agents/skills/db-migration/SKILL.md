---
name: db-migration
description: Generates and applies Alembic database migrations for ApexPOS. Use when database models are modified, new tables are added, or schema changes are needed.
---

# Database Migrations with Flask-Migrate

## When to use this skill
- A new model has been added to `backend/app/models/`.
- Columns have been added, removed, or modified on an existing model.
- Database schema needs to be synchronized with model definitions.

## Workflow
1. [ ] **Pre-flight check**: Verify the new/modified model is imported in `app/models/__init__.py`.
2. [ ] **Activate environment**: Activate the Python virtual environment.
3. [ ] **Generate migration**: Auto-generate migration comparing models to active DB schema.
4. [ ] **Inspect migration**: Review the generated file for correctness.
5. [ ] **Apply migration**: Upgrade the database.
6. [ ] **Verify**: Confirm tables match updated model files.

## Instructions

### 1. Pre-Flight: Model Registration Check
Before generating a migration, verify that your model is properly registered:

```python
# In backend/app/models/__init__.py — MUST contain:
from app.models.your_entity import YourEntity

__all__ = [
    # ... existing models ...
    'YourEntity'
]
```

> **CRITICAL**: If the model is not imported here, Flask-Migrate will NOT detect it and the migration will be empty.

### 2. Environment Setup
Set the working directory (`Cwd`) to `backend/` and activate the virtual environment:

* **Windows PowerShell**:
  ```powershell
  . venv/Scripts/Activate.ps1
  ```
* **Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```

### 3. Generate Migration
Auto-generate a migration script comparing models to the active database schema:
```bash
flask db migrate -m "Description of changes"
```

Use descriptive messages, e.g.:
- `"Add suppliers table"`
- `"Add barcode column to products"`
- `"Add audit fields to shifts"`

### 4. Inspect Migration
Review the generated migration file in `backend/migrations/versions/`:
- Verify `upgrade()` contains the expected `CREATE TABLE` or `ALTER TABLE` operations.
- Verify `downgrade()` correctly reverses the changes.
- Check that column types match your model definitions (especially `Numeric(10, 2)` vs `Numeric(10, 3)`).

### 5. Apply Migration
Upgrade the PostgreSQL database to the latest migration:
```bash
flask db upgrade
```

### 6. First-Time Setup
If this is a brand-new project without a `migrations/` folder:
```bash
flask db init
```
This creates the Alembic migrations directory structure. Only needed once per project.

### 7. Migration Chain
Current migration history (9 revisions):
1. Initial schema (categories, products, users, sales, etc.)
2. Add discounts table
3. Add shifts table
4. Add audit who/when/where fields
5. Add updated_at fields
6. Add stores table and employee profiles
7. Add store auditing
8. Add UOM and decimal quantities
9. Add min_sale_qty

> **NEVER** delete or reorder migration files — they form a dependency chain.
