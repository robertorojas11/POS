# ApexPOS: Manager User Manual

This manual explains product administration, shift drawer auditing, cashier monitoring, and operational reports for Store Managers.

---

## 🖥️ 1. Manager Dashboard Monitoring

The Dashboard (`/dashboard`) is the central control screen for tracking active register terminals.

### Live Shift Grid
Managers can view a live table of all open registers:
- **Cashier Name**: The operator logged in.
- **Terminal & Store Location**: Metadata representing where the sale is being processed.
- **Opening Cash**: Starting drawer amount.
- **Cash Sales**: Cumulative cash collected during the shift.
- **Expected Cash**: Current calculated cash that should be physically present in the drawer (`Opening Cash + Cash Sales`).

### 👥 Shift Employees Directory
Located on the dashboard, the **Shift Employees Directory** displays a list of all operators/cashiers assigned to the manager's shift turn.
- **Active Status**: Cashiers who have an open shift are marked with a green dot and **Active** status.
- **Offline Status**: Cashiers who do not have an open shift are marked with a gray dot and **Offline** status.
- This panel allows real-time operational auditing of who is active on which register.

### ⚠️ Cash Drop Alerts (Over $1,000 Threshold)
To maintain security and limit cash exposure, the system monitors drawer levels in real-time.
- If a drawer's **Expected Cash** exceeds **$1,000.00**, a blinking crimson warning banner will appear next to that cashier's shift entry.
- **Required Action**:
  1. Walk to the specified terminal.
  2. Perform a cash sweep (e.g. withdraw $800 from the register to place in the safe).
  3. Note: The warning banner alerts you of the excess cash. Cash drops do not end the shift turn.

---

## 📦 2. Catalog & Product Inventory Management

Managers configure the product catalog from the **Products** screen (`/products`).

### Adding/Editing Products
1. Click **Add Product** (or select **Edit** on an existing item).
2. Input the basic details:
   - **SKU**: Unique catalog identifier (must be unique).
   - **Barcode**: Scanner representation.
   - **Name & Description**.
   - **UOM (Unit of Measurement)**: Select how the product is sold:
     - `pieces` (discrete counts)
     - `kilograms`, `grams` (mass weights)
     - `liters`, `gallons` (liquid volume)
     - `pounds` (weight)
3. Set the financial metrics:
   - **Price**: Retail price charged to customer (excluding tax).
   - **Cost Price**: Business wholesale cost (used to calculate profit margins).
4. Configure stock levels:
   - **Stock Quantity**: The count currently in stock. Supports **3 decimal places** for weighted inventory (e.g. `250.750` kg).
   - **Min Stock Level**: The threshold that triggers low-stock alerts.
5. Click **Save**.

> [!TIP]
> Saving modifications automatically invalidates all terminal caches and broadcasts an instant Server-Sent Events (SSE) reload signal to all active cashier screens, prompting them to refresh their local catalogs.

---

## 📊 3. Auditing & Reports

Managers verify transactions and review sales metrics from the `/reports` and transaction history modules:
* **Sale History**: Search, filter, and review completed invoices.
* **Shift Auditing**: Check closed shift logs to review actual vs. expected cash counts and investigate cashier variances.
* **Hourly Reports**: Review sales spikes throughout the day to optimize staffing schedules.
