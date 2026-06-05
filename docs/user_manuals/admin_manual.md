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

### 👥 Store Workers & Employee Administration
Admin users can manage the active staff directory and assign them to specific stores (sucursales) from the **Admin View** (`/admin`).

#### Tab 1: Employees Directory
This interface lists all employees registered in the system:
* **Workers Directory Details**: Displays the employee's username, full name, email, phone number, role, assigned store/sucursal, and shift status (Active/Offline).
* **Temporary Access Status**: Shows a warning label `Needs password change` next to the username if the employee has not yet logged in and changed their temporary password.
* **Adding a New Employee**:
  1. Click **Add Employee** to open the registration form.
  2. Input: **First Name**, **Last Name**, **Second Last Name (Optional)**, **Email**, **Contact Phone (Optional)**, **Role (Admin, Manager, Operator)**, and **Assigned Store**.
  3. **Automated Username Generation**: The system automatically generates a unique username using the format:
     `firstname.first_surname_letter.xy`
     * `firstname` is the employee's first name (lowercase, spaces removed).
     * `first_surname_letter` is the first letter of their last name (lowercase).
     * `x` is the unique store identifier code of their assigned sucursal.
     * `y` is a 2-character random alphanumeric suffix to guarantee uniqueness.
     * Example: `john.d.la82` (where `la` is the Los Angeles branch code).
  4. **Temporal Password**: The system generates a copyable temporary password (e.g. `Temp8472`) and displays it in a green success banner for the admin.
  5. **Force Password Reset**: On their very first login, the employee is greeted by a non-dismissible password change overlay. They must set a secure password of at least 4 characters to unlock POS access.

#### Tab 2: Sucursales (Stores)
Manage the business physical locations that employees are assigned to:
* **Store Parameters**:
  - **Code**: Unique code identifier (e.g., `la`, `ny`, `mx`). This code is used as the prefix when generating usernames for users assigned to this branch.
  - **Name**: Store name (e.g., "Los Angeles Downtown", "New York Flagship").
  - **Location**: City or general region.
  - **Address**: Detailed physical location.
* **Registering a Store**: Click **Add Store**, enter the parameters, and click **Save**.

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
