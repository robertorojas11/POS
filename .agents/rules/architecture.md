# Architecture Rules

This document defines the architectural boundaries and organization requirements for the ApexPOS project.

---

## 1. Folder Structure

### Backend (`backend/`)
```
backend/
├── app/
│   ├── __init__.py          # Application factory (create_app) — ONLY place to register blueprints
│   ├── config.py            # Config classes — ONLY place for environment config
│   ├── extensions.py        # Extension singletons — ONLY place to instantiate db, jwt, redis
│   ├── models/              # SQLAlchemy model classes — ONE file per domain entity
│   │   └── __init__.py      # MUST re-export all models for Flask-Migrate discovery
│   ├── routes/              # Flask Blueprints — ONE file per resource domain
│   ├── services/            # Business logic classes — complex operations only
│   └── utils/               # Cross-cutting utilities (decorators, helpers)
├── tests/                   # unittest test cases — ONE file per domain
├── migrations/              # Alembic auto-generated migrations — NEVER edit manually unless necessary
├── seed.py                  # Development data seeder
└── run.py                   # Dev server entry point
```

### Frontend (`frontend/`)
```
frontend/
└── src/
    ├── main.js              # App bootstrap, global interceptors — DO NOT add business logic here
    ├── App.vue              # Minimal root — ONLY contains <router-view />
    ├── style.css            # Design system (CSS variables, global classes) — SINGLE source of truth for design tokens
    ├── router/index.js      # Route definitions + navigation guards
    ├── store/               # Pinia stores — ONE file per domain
    ├── views/               # Page-level components — ONE per route
    ├── components/          # Reusable UI components
    │   └── layouts/         # Layout wrappers (MainLayout)
    └── utils/               # Client-side utilities (IndexedDB wrapper)
```

## 2. Layer Boundaries

### Backend Layers (top → bottom)
```
Routes (Controllers) → Services → Models → Database
                    ↘ Utils (cross-cutting)
```

**Rules**:
- Routes MAY call Services or Models directly.
- Routes MUST NOT contain complex business logic (>20 lines of non-CRUD logic → extract to Service).
- Services MUST NOT import from Routes.
- Models MUST NOT import from Routes or Services.
- Utils MUST NOT import from Routes, Services, or Models (except the User model for auth).

### Frontend Layers
```
Views → Components (presentation)
Views → Stores (data/state)
Stores → Axios (API)
Stores → IndexedDB (offline cache)
```

**Rules**:
- Views MUST use stores for all API calls — NEVER call axios directly from a view or component.
- Components MUST be pure presentation — receive data via props, emit events for mutations.
- Stores are the ONLY layer that imports `axios`.

## 3. Dependency Direction
- Frontend depends on Backend (via REST API through Vite proxy).
- Backend NEVER depends on Frontend.
- Models are the foundation — everything else depends on them.
- Circular imports between route files are FORBIDDEN.

## 4. Feature Organization
New features follow the vertical slice pattern:
```
Model → Migration → Route → Test → Store → View → Router Config → Sidebar Link
```
Every feature MUST have representation in ALL applicable layers.
