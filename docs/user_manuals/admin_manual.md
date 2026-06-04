# ApexPOS: Administrator User Manual

This manual explains user provisioning, promotional discount configurations, system architecture maintenance, and database migration commands for IT Administrators.

---

## 👥 1. User Provisioning & Roles

ApexPOS enforces access security using a normalized, relational role structure.

### Role Hierarchy
There are three user types, defined as follows:

| User Type Name | Database ID | Access Scope |
| :--- | :---: | :--- |
| **Admin** | `1` | Complete system access. Manage users, create discounts, adjust system settings, audit transactions. |
| **Manager** | `2` | Modify products, review sales history, monitor shifts/cash drawers, view store reports. |
| **Operator** | `3` | Start/end own shifts, register customers, validate coupons, and checkout sales. |

### 👥 Store Workers Directory
Admin users have access to the **Store Workers Directory** on their Dashboard.
- Unlike the Manager's view (which only shows register Operators), the Admin's directory panel lists **all** store workers, including other Admins, Managers, and operators/cashiers.
- Displays employee username, email, system role, and real-time **Active** (with green indicator dot) or **Offline** status based on active shifts.

### Provisioning a New User
To register a new employee:
1. Make a POST request to `/api/auth/register` (or use the admin registration interface).
2. Required fields:
   - `username`: Unique username string.
   - `email`: Valid email address.
   - `password`: Secure password.
   - `role`: Role string (one of `'admin'`, `'manager'`, `'operator'`).
3. The system maps the string role to the correct relational database `UserType` record.

---

## 🎟️ 2. Discount & Promotion Setup

Discount codes are created globally by administrators and are synchronized to registers for immediate cashier lookup.

### Creating a Promotion Code
1. Use the Discount Management tool or POST to `/api/sales/discounts`.
2. Required fields:
   - **Code**: Text string containing the coupon lookup (e.g. `SUMMER50`). The code is converted to UPPERCASE.
   - **Type**: Choose between:
     - `fixed`: Deducts a flat currency amount (e.g., `$5.00` off).
     - `percent`: Deducts a percentage from the subtotal (e.g., `15.0%` off).
   - **Value**: Number representing the reduction.
3. **Safety Constraints**:
   - Discount values cannot be negative.
   - Percentage discounts cannot exceed `100.0%`.
   - Code strings must be unique.

---

## 💾 3. System Maintenance & Migrations

If database structures are modified or need to be initialized on a new terminal machine:

### DB Schema Upgrades (Alembic)
1. Set the database connection environment variables.
2. In the `backend` directory, run:
   ```bash
   flask db upgrade
   ```
3. This applies the latest migrations (including columns for decimal units of measurement and shift sessions).

### Seeding Initial Data
To populate the database tables with standard user types, categories, initial products, and test discounts, run:
```bash
python seed.py
```
*(Executes user type insertions and links default manager and operator credentials, setting admin password to `admin` for local testing)*.
