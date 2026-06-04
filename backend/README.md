# ApexPOS: Backend Flask API Server

The backend of ApexPOS is a modern, modular Flask REST API server designed to support atomic inventory calculations, cashier shift management, and secure role-based access.

---

## 1. Architecture Overview

The backend uses the **Application Factory** pattern to instantiate configuration states cleanly and prevent circular dependencies:

```
backend/
├── app/
│   ├── models/        # SQLAlchemy Database Models
│   ├── routes/        # Blueprint Route Controllers
│   ├── services/      # Business & Transaction Services
│   ├── utils/         # Helpers & Custom Decorators
│   ├── config.py      # App Configurations (Dev, Testing, Prod)
│   ├── extensions.py  # Extension registries (DB, JWT, Cache)
│   └── __init__.py    # App Factory constructor
├── migrations/        # Alembic DB Migration Revisions
├── tests/             # PyUnit Integration and Unit Tests
├── run.py             # App execution entrypoint
├── seed.py            # Development database seeder
└── requirements.txt   # Third-party dependencies
```

---

## 2. Security & Modular Permissions

Features are locked down modularly based on normalized `UserType` roles:
1. **Admin**: Has complete control, including creating discounts and managing products.
2. **Manager**: Has report auditing and inventory catalog management privileges.
3. **Operator (Cashier)**: Restricted to register checkouts and self-shift operations.

Access control is enforced using the `@requires_user_type(*roles)` decorator, which intercepts JWT tokens and validates user profiles before routing.

---

## 3. Database Schema & Audit Trail

The backend uses PostgreSQL (with SQLite for local testing) managed via SQLAlchemy.

### Audit Columns (Who, When, Where)
To ensure complete transparency and data integrity:
* **Who**: Tables include `created_by_id` and `updated_by_id` foreign keys linking back to `users.id`. Users record `last_login` timestamps and `last_login_ip` addresses.
* **When**: Tables track `created_at` and `updated_at` timestamps in UTC.
* **Where**: POS `sales` and `shifts` track `terminal_id` (POS register terminal identifier), `store_location`, and `device_ip`.

### Cashier Turns & Shifts
The `shifts` table uses **UUID** identifiers to avoid predictable sequence guessing. It implements:
* **Starting Cash**: Opening drawer balance.
* **Ending Cash**: Counted cash upon closing turn.
* **Drawer Variance**: Compares actual drawer cash against expected totals (opening cash + cash sales).

---

## 4. Development Setup

### Prerequisites
* Python 3.11+
* Active PostgreSQL & Redis instances (or fallbacks for local development)

### Installation
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
2. Install third-party packages:
   ```bash
   pip install -r requirements.txt
   ```

### Seeding Data
To populate the database with categories, default users (admin, manager1, cashier1), and products:
```bash
python seed.py
```

### Running Tests
Execute the PyUnit test discovery to run unit and integration suites:
```bash
$env:FLASK_CONFIG="testing"; $env:TEST_DATABASE_URL="sqlite:///:memory:"; python -m unittest discover -s tests -p "test_*.py"
```

### Running Server
Launch the Flask development server:
```bash
python run.py
```

---

## 5. Database Migrations

Database revisions are managed using **Flask-Migrate** (Alembic):
1. **Check or Apply Upgrades**:
   ```bash
   flask db upgrade
   ```
2. **Generate New Schema Revisions**:
   ```bash
   flask db migrate -m "Description of changes"
   ```
