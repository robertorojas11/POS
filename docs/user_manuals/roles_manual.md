# ApexPOS: Roles & Capabilities Manual

This manual provides a detailed reference of user roles, access scopes, and functional capabilities within the **ApexPOS** platform. It outlines the restrictions enforced on both the frontend UI and the backend API endpoints.

---

## 👥 1. Roles Overview

ApexPOS uses a normalized database role structure to segregate duties among store staff. The three primary roles are:

1. **Admin (Administrator)**: IT/Corporate administrator with full control over system configuration, physical branches, and staff provisioning.
2. **Manager (Store Manager)**: Operational leader responsible for catalog configuration, inventory management, shift audits, and cash drawer security.
3. **Operator (Cashier)**: Frontend staff member executing sales transactions, customer registration, and register checkouts.

---

## 🔐 2. Capabilities Matrix

| Functional Feature | Admin | Manager | Operator (Cashier) |
| :--- | :---: | :---: | :---: |
| **POS Sales Register (`/pos`)** | Yes | Yes | Yes |
| **Open / Close Personal Shift** | Yes | Yes | Yes |
| **Apply Coupon Discounts** | Yes | Yes | Yes |
| **View Store Reports (`/reports`)** | Yes | Yes | No |
| **Audit Closed Cashier Shifts** | Yes | Yes | No |
| **Monitor Live Cash Drawers** | Yes | Yes | No |
| **Add / Edit Catalog Products** | Yes | Yes | No |
| **Create Global Discount Codes** | Yes | No | No |
| **Manage Stores / Sucursales** | Yes | No | No |
| **Register & Assign Employees** | Yes | No | No |

---

## ⚙️ 3. Detailed Role Capabilities

### 👑 Admin (Administrator)
* **Access Scope**: Full System Access (Frontend `/admin` and all backend blueprints).
* **Key Capabilities**:
  * **Sucursales (Stores) Management**: Create physical branches, configure branch codes, location names, and physical addresses.
  * **Employee Provisioning**: Register staff profiles, assign them to branches, auto-generate unique credentials, and create copyable temporary passwords.
  * **Global Directory View**: Access the full workers directory on the dashboard, viewing the current active/offline status of all staff members (Admins, Managers, Operators).
  * **Discount Configuration**: Authorize and create global discount codes (percentage/fixed promotions).
  * **Auditing & Reporting**: Review full store sales reports, hourly metrics, and shift audits.
  * **Catalog Administration**: Full capabilities to add, edit, or deactivate products.
  * **System Maintenance**: Execute database schema updates (migrations) and seed configuration.

### 👔 Manager (Store Manager)
* **Access Scope**: Operations Dashboard, Product Catalog, Reports, and Personal Shift (no access to `/admin`).
* **Key Capabilities**:
  * **Catalog & Inventory Control**: Add new products, configure units of measurement (UOM), edit prices/cost metrics, and adjust stock quantities.
  * **Cash Drawer Auditing**: Inspect the expected vs. actual closing balances of cashiers. Review cashier cash variances and sign off on shifts.
  * **Live Drawer Monitoring**: Track expected cash in registers in real-time. Receives crimson warnings for registers exceeding the **$1,000 cash threshold** to prompt cash drops.
  * **Shift Employee Directory**: View real-time active status of all operators/cashiers assigned to their shift.
  * **NO Access**: Cannot access the `/admin` view, register new employees, assign branches, or configure global promotional codes.

### 🛒 Operator (Cashier)
* **Access Scope**: POS Sales Register and Personal Shift Dashboard (no access to `/admin`, `/reports`, `/products` modification, or manager dashboards).
* **Key Capabilities**:
  * **POS Checkout**: Scan barcodes, add items manuals from the catalog, adjust line item quantities (including decimal values for bulk/weighted items), and checkout using cash or card.
  * **Shift Control**: Input starting cash to open their drawer, and input final actual cash count to close their shift.
  * **Offline Resilience**: Complete sales offline using local IndexedDB caching. Local stock levels are auto-deducted, and queued offline transactions automatically sync when network connection is restored.
  * **Coupon Lookup**: Enter valid codes to apply cart discounts.
  * **Cart Maintenance**: Remove specific items or clear the entire cart.
  * **NO Access**: Blocked by frontend routing guards from accessing administrative views. Frontend Add/Edit product buttons are completely hidden. The backend enforces user type decorators on REST endpoints (`/api/products` POST/PUT, `/api/auth/employees` POST, `/api/store` CRUD) returning `403 Access Denied` if an Operator attempts to access them.
