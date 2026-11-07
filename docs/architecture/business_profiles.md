# One template, many businesses

This repo is the template. Each business gets its **own deployment** (own database, own `.env`) of the same code.
What changes between a grocery, a toy store, a bar and a restaurant is configuration plus a few optional features, not a fork.

## Decisions

| # | Decision | Why |
|---|----------|-----|
| 1 | **Single-tenant: one deployment per business.** No `tenant_id` column anywhere. | Multi-tenant adds a filter to every query and one leak bug exposes another business's sales. A POS deployment is small; running one stack per client is cheaper than that risk. |
| 2 | **`BUSINESS_TYPE` env var** (`retail`, `restaurant`, `bar`) picks a profile in `backend/app/business.py`. | One switch, one file. The frontend reads `GET /api/config` and hides features that are off. |
| 3 | **Retail covers grocery, toys, hardware, general stores.** | They differ only in data: `uom` (pieces, kilograms) and `min_sale_qty` per product already express "sold by weight" vs "by piece". No new model needed. |
| 4 | **Restaurant and bar need new models, built when the first such client signs.** | They need open tabs per table, item modifiers, tips, kitchen tickets, age check. None is built, so those flags are `False`. Building them without a real client means guessing the workflow. |
| 5 | **Core stays the same for every type:** products, stock, sales, shifts, users, audit. New features are additive tables plus a flag, never a change to `Sale`. | Keeps the money path (checkout, shift cash count) one tested code path for everyone. |
| 6 | **Server owns every number.** Tax rate (`TAX_RATE`), prices and discounts are computed in `SalesService`; the till only sends product ids, quantities and a discount *code*. | A modified till can no longer give free goods. |
| 7 | **Manual (typed-in) discounts are Manager/Admin only.** Operators use discount codes. | Free-form cashier discounts are the classic POS theft route. To allow it per business, edit `MANUAL_DISCOUNT_ROLES` in `sales_service.py`. |
| 8 | **Per-deployment settings live in `.env`:** `BUSINESS_TYPE`, `BUSINESS_NAME`, `CURRENCY`, `TAX_RATE`, `TIMEZONE`, `CORS_ORIGINS`. See `.env.example`. | Nothing business-specific is hard-coded. |
| 9 | **Tax is one flat rate, added on top (US style).** | Per-product tax classes and tax-included pricing (common outside the US) are not built. Add `Product.tax_rate` and a `TAX_INCLUDED` setting when a client needs them. |
| 10 | **Offline sales are never deleted.** A sale the server rejects stays in the till's IndexedDB marked `failed` with the reason, for a manager. | The customer already paid. |

## Adding a feature for a business type

1. Add the tables with a migration (additive only).
2. Add the routes. Reuse `SalesService.process_checkout`; extend it, do not copy it.
3. Flip the flag to `True` in `PROFILES` for the types that use it.
4. In the frontend, show the screen only when `cartStore.businessConfig.features.<flag>` is true.

## Roadmap per type (not built)

- **Restaurant:** `tables`, `table_tabs` (open order per table, many items added over time, paid at the end), `modifiers` on `SaleItem`, `tips`, kitchen ticket printing.
- **Bar:** tabs (open a tab on a card), `age_check`, happy-hour price rules, pours (fractional stock per bottle).
- **Grocery at scale:** barcode label printing, scale integration, tax classes.
