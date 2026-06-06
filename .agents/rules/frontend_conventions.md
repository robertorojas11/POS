# Frontend Conventions

Rules governing Vue 3 frontend development in ApexPOS.

---

## 1. SFC Structure
Every `.vue` file MUST follow this section order:
```
<template> → <script setup> → <style scoped>
```
- Always use `<script setup>` (Composition API shorthand).
- Always use `<style scoped>` to prevent CSS leaks.

## 2. File Naming
| Artifact | Convention | Example |
|----------|-----------|--------|
| Views | PascalCase + `View` suffix | `ProductsView.vue` |
| Components | PascalCase | `ProductCard.vue`, `MetricCard.vue` |
| Stores | camelCase | `products.js`, `auth.js` |
| Utils | camelCase | `indexedDb.js` |

## 3. Component Standards
- Define props with `defineProps()` including `type` and `default`/`required`.
- Define emits with `defineEmits()` as an array of event names.
- Use `lucide-vue-next` for all icons — never use raw SVGs or other icon libraries.
- Computed properties via `computed()` from Vue.

## 4. State Management
- ALL global state lives in Pinia stores under `src/store/`.
- Stores use **Options API** style (`state`, `getters`, `actions`).
- API calls are ONLY made inside store actions — never in components or views.
- Error handling: `err.response?.data?.error || 'Fallback message'`.
- Loading states: Set `this.loading = true` at action start, reset in `finally`.

## 5. Routing
- All authenticated routes are children of the MainLayout route.
- Use lazy imports: `component: () => import('@/views/SomeView.vue')`.
- Meta flags: `requiresAuth`, `guestOnly`, `requiresAdmin`.
- Navigation guard in `router/index.js` enforces auth and role checks.

## 6. Design System
### CSS Variables (from `style.css`)
- **Backgrounds**: `--bg-app`, `--bg-card`, `--bg-sidebar`
- **Text**: `--text-primary`, `--text-secondary`, `--text-muted`
- **Accents**: `--accent-lime`, `--accent-success`, `--accent-warning`, `--accent-danger`
- **Borders**: `--border-color`, `--border-focus`
- **Radii**: `--radius-sm` (8px), `--radius-md` (12px), `--radius-lg` (16px), `--radius-xl` (20px)
- **Shadows**: `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-premium`
- **Transitions**: `--transition-fast` (0.15s), `--transition-normal` (0.25s)

### Global Classes
- `.premium-card` — Card containers
- `.pos-btn` / `.pos-btn-accent` / `.pos-btn-secondary` / `.pos-btn-danger` — Buttons
- `.pos-input` / `.pos-input.with-left-icon` — Form inputs

### Rules
- NEVER hardcode colors — always use CSS variables.
- NEVER override `font-family` — `Outfit` is set globally.
- Use spacing multiples of 4px.
- Hover effects: `translateY(-1px)` or `translateY(-2px)` with shadow elevation.

## 7. API Communication
- Always use relative URLs: `/api/...` (Vite proxy forwards to Flask).
- Auth headers are set globally via axios interceptor in `main.js`.
- Terminal ID sent via `X-Terminal-Id` header (auto-set in `main.js`).

## 8. Offline Support
- IndexedDB via `utils/indexedDb.js` for local caching.
- Products and categories cached locally for offline POS operation.
- Offline sales queued in `sales_queue` store and synced on reconnect.
