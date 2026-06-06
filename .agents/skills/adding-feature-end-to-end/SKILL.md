---
name: adding-feature-end-to-end
description: Orchestrates the full-stack implementation of a new feature in ApexPOS, from database model to API to frontend. Use when building a complete new capability that spans backend and frontend.
---

# Adding a Feature End-to-End

## When to use this skill
- Implementing a complete new feature (e.g., "Supplier Management", "Expense Tracking").
- Adding a new CRUD resource that needs model + API + store + view.
- Building a feature that touches multiple layers of the stack.

## Workflow
1. [ ] **Define requirements**: Entity fields, relationships, API endpoints, UI screens.
2. [ ] **Backend: Create model** → Use `creating-backend-models` skill.
3. [ ] **Backend: Generate migration** → Use `db-migration` skill.
4. [ ] **Backend: Create endpoints** → Use `creating-api-endpoints` skill.
5. [ ] **Backend: Write tests** → Use `writing-backend-tests` skill.
6. [ ] **Backend: Run tests** → Use `running-backend-tests` skill.
7. [ ] **Frontend: Create Pinia store** → Use `creating-pinia-stores` skill.
8. [ ] **Frontend: Create view page** → Use `creating-vue-views` skill.
9. [ ] **Frontend: Create components** → Use `creating-vue-components` skill (if needed).
10. [ ] **Frontend: Add route** → Add to `frontend/src/router/index.js`.
11. [ ] **Frontend: Add sidebar link** → Add to `AppSidebar.vue`.
12. [ ] **Frontend: Build verify** → Use `building-frontend` skill.
13. [ ] **Documentation**: Update relevant docs if needed.

## Instructions

### 1. Implementation Order
Always follow this exact order to avoid broken dependencies:

```
Model → Migration → Route → Test → Store → View → Route Config → Sidebar → Build
```

### 2. Backend Checklist

#### Model (`backend/app/models/<entity>.py`)
- [ ] Define `__tablename__` (plural snake_case)
- [ ] Add domain columns with correct types
- [ ] Add all 4 audit columns (`created_at`, `updated_at`, `created_by_id`, `updated_by_id`)
- [ ] Add `creator`/`updater` relationships
- [ ] Add `to_dict()` method
- [ ] Register in `backend/app/models/__init__.py`

#### Migration
- [ ] Run `flask db migrate -m "Add <entity> table"`
- [ ] Inspect generated migration in `backend/migrations/versions/`
- [ ] Run `flask db upgrade`

#### Routes (`backend/app/routes/<entity>.py`)
- [ ] Create blueprint: `<entity>_bp = Blueprint('<entity>', __name__)`
- [ ] Implement CRUD: GET list, GET by ID, POST, PUT, DELETE
- [ ] Add `@jwt_required()` on all endpoints
- [ ] Add `@requires_user_type(...)` on write endpoints
- [ ] Set `created_by_id` / `updated_by_id` from `get_jwt_identity()`
- [ ] Call `RedisService.invalidate_products_cache()` if product-related
- [ ] Register blueprint in `backend/app/__init__.py`

#### Tests (`backend/tests/test_<entity>.py`)
- [ ] Test CRUD operations (201, 200, 200, 200)
- [ ] Test validation (400)
- [ ] Test authorization (401, 403)
- [ ] Test audit trail fields

### 3. Frontend Checklist

#### Pinia Store (`frontend/src/store/<entity>.js`)
- [ ] Define state: `items[]`, `loading`, `error`
- [ ] Implement CRUD actions with axios
- [ ] Use relative URLs: `/api/<entity>`

#### View (`frontend/src/views/<Entity>View.vue`)
- [ ] Use `<script setup>` composition API
- [ ] Import store with `use<Entity>Store()`
- [ ] Create list/table display
- [ ] Create add/edit modal
- [ ] Add role-based UI gating
- [ ] Use design system classes (`premium-card`, `pos-btn-accent`, `pos-input`)
- [ ] Use `<style scoped>` with CSS variables

#### Router (`frontend/src/router/index.js`)
- [ ] Add route as child of MainLayout:
```javascript
{
    path: '<entity>',
    name: '<entity>',
    component: () => import('@/views/<Entity>View.vue'),
    meta: { requiresAdmin: true }  // if admin-only
}
```

#### Sidebar (`frontend/src/components/AppSidebar.vue`)
- [ ] Add navigation link with appropriate lucide icon
- [ ] Add role guard if needed (`v-if="authStore.isAdmin"`)

### 4. File Map for a Feature Named "suppliers"
```
backend/app/models/supplier.py          ← Model
backend/app/models/__init__.py          ← Registration
backend/migrations/versions/xxx.py      ← Migration
backend/app/routes/supplier.py          ← Blueprint
backend/app/__init__.py                 ← Blueprint registration
backend/tests/test_supplier.py          ← Tests
frontend/src/store/suppliers.js         ← Pinia store
frontend/src/views/SuppliersView.vue    ← Page view
frontend/src/router/index.js            ← Route addition
frontend/src/components/AppSidebar.vue  ← Sidebar link
```

## Why This Skill Exists
- **Protects**: Ensures every feature follows the complete implementation path and nothing is missed.
- **Prevents**: Orphaned models without routes, stores without views, views without routes.
- **Evolution**: As the project adds more cross-cutting concerns (logging, audit logs, SSE events), add them to this checklist.
