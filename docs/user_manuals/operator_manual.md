# ApexPOS: Operator (Cashier) User Manual

This manual explains daily cash register operations, shift cycles, checkout workflows, and offline resilience for POS Operators (Cashiers).

---

## 🕒 1. Shift Cycle Operations

Every sales transaction must be linked to an active shift session for accounting auditability.

### Starting Your Shift (Open Drawer)
1. Log in to the terminal with your Operator credentials.
2. The dashboard will request your starting drawer cash.
3. Count the physical cash in the drawer and input the amount (e.g. `150.00`).
4. Click **Start Shift**. You can now navigate to the POS register screen.

> [!IMPORTANT]
> Always verify the drawer cash physically before opening. Starting with an incorrect amount will result in a shift variance discrepancy when closing the shift.

### Closing Your Shift (Close Drawer)
1. Navigate to the shift control widget on the Dashboard.
2. Count the total physical cash in the drawer (including the starting cash and all cash sales).
3. Input the total amount in the **Actual Cash** field.
4. Click **Close Shift**.
5. The system will display your **Shift Turn Report** showing your starting cash, card/cash sales, expected cash, and any **Variance** (surplus or shortage).

---

## 🛒 2. POS Checkout Operations

The registry screen (`/pos`) is where you process customer sales.

```
+-------------------------------------------------------------+
| [ Barcode Search / Selector ]                [Online/Green] |
| +-------------------------+ +-----------------------------+ |
| | SKU / Product Name      | | Cart Summary                | |
| +-------------------------+ | - Apples (1.500 kg)  $4.50  | |
| | Apples [1 kg]     $3.00 | | - Rice   (2.000 kg)  $6.00  | |
| | Milk   [1 L]      $2.50 | |                             | |
| | Soda   [1 piece]  $1.50 | | Discount Code: [ SPRING20 ] | |
| +-------------------------+ +-----------------------------+ |
|                             | Subtotal:            $10.50 | |
|                             | Discount Applied:    -$2.10 | |
|                             | Tax (8.25%):          $0.69 | |
|                             | Total:                $9.09 | |
|                             +-----------------------------+ |
|                             | [ PAY CASH ]   [ PAY CARD ] | |
+-------------------------------------------------------------+
```

### Adding Products to Cart
- **Barcode Scanner**: Position your cursor in the product search box and scan the barcode. The product will instantly be added to the cart.
- **Manual Catalog Selector**: Click on product categories to filter, and click a product card to add it to the cart.

### Handling Decimal Units of Measurement (UOM)
For bulk, weighted, or volume products (e.g., Kilograms, Grams, Liters, Gallons, Pounds):
1. Locate the product in the active cart list.
2. The quantity input field allows **3 decimal places** of precision.
3. Use the keyboard to input the exact weight/volume (e.g., `1.545` for 1.545 kg of apples).
4. The cart subtotal will automatically recalculate.

### Applying Coupon Discounts
1. In the checkout panel, locate the **Discount Code** input field.
2. Input the promotional coupon code (e.g. `SPRING20`) and click **Apply**.
3. If online, the app verifies with the backend API. If offline, the app scans the local IndexedDB promotions cache.
4. If valid, the cart total will instantly display the applied reduction.

---

## 📶 3. Operating Offline (No Connection)

ApexPOS is designed to continue operations even if the store network goes down.

### Understanding Status Banners
- **Online (Green Indicator)**: Normal server connection. Sales post directly to the database.
- **Offline (Amber Indicator)**: Network connection lost. The app enters local resilient mode.

### What Happens Offline?
* Barcode scanning, product lookups, UOM decimal adjustments, and cart suspensions continue to function normally using local data cached in **IndexedDB**.
* Checking out will generate a local temporary invoice labeled `OFFLINE-INV-<timestamp>-<rand>`.
* The system deducts the item quantities from the local stock catalog automatically to prevent you from selling items that have run out of stock.
* Transactions are saved securely to the browser's local queue. The count of unsynced sales is shown in the header status indicator.

> [!TIP]
> Do not close or clear browser cookies while transactions are queued in offline mode, as they are saved in the browser's local memory.

### Synchronizing Offline Sales
1. Once connection is restored, the status banner switches to **Online (Green)**.
2. The system automatically attempts to sync queued sales in the background.
3. You can also manually trigger synchronization by clicking the **Sync Queue** button in the header.
4. Once completed, your catalog inventory levels are refreshed from the server.
