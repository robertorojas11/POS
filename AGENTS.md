# Agent Instructions Router

Welcome, AI Agent! This file acts as the primary router for your operations in this codebase. Refer to the directory structures below to improve task outcomes, execute codebase commands, and maintain strict standards.

---

## 1. Project Context
- **Project Name**: ApexPOS
- **Core Structure**: Frontend is a Vue 3 SPA client in `frontend/`. Backend is a Flask API server in `backend/`.
- **Tech Stack**: Vue 3 + Vite + Pinia | Flask + SQLAlchemy + Flask-Migrate | PostgreSQL + Redis | Docker Compose
- **Primary Rules**: Always review the code guidelines in the Rules folder:
  - [coding_standards.md](file:///D:/ERP/POS/.agents/rules/coding_standards.md): Master reference for naming, patterns, and conventions.
  - [architecture.md](file:///D:/ERP/POS/.agents/rules/architecture.md): Folder structure, layer boundaries, dependency direction.
  - [backend_conventions.md](file:///D:/ERP/POS/.agents/rules/backend_conventions.md): Flask patterns, model schemas, route structure, service layer.
  - [frontend_conventions.md](file:///D:/ERP/POS/.agents/rules/frontend_conventions.md): Vue SFC standards, Pinia stores, design system, routing.
  - [api_contracts.md](file:///D:/ERP/POS/.agents/rules/api_contracts.md): Endpoint naming, request/response formats, status codes, auth.
  - [database_standards.md](file:///D:/ERP/POS/.agents/rules/database_standards.md): Migration rules, naming, audit fields, Redis key patterns.

---

## 2. Capabilities & Skills (How to perform tasks)
When instructed to run specific developer operations, view the corresponding files in the `.agents/skills/` directory using your file-viewing tools, making sure to flag them as skill execution files (set `IsSkillFile: true`):

### Operational Skills
- **Running Tests**: Refer to [running-backend-tests/SKILL.md](file:///D:/ERP/POS/.agents/skills/running-backend-tests/SKILL.md) to check backend endpoint health.
- **Database Schema Upgrades**: Refer to [db-migration/SKILL.md](file:///D:/ERP/POS/.agents/skills/db-migration/SKILL.md) to initialize or deploy Alembic DB migrations.
- **Compiling Frontend Assets**: Refer to [building-frontend/SKILL.md](file:///D:/ERP/POS/.agents/skills/building-frontend/SKILL.md) to verify Vue component compilation.

### Creation Skills (Building New Features)
- **New Database Models**: Refer to [creating-backend-models/SKILL.md](file:///D:/ERP/POS/.agents/skills/creating-backend-models/SKILL.md) for SQLAlchemy model patterns.
- **New API Endpoints**: Refer to [creating-api-endpoints/SKILL.md](file:///D:/ERP/POS/.agents/skills/creating-api-endpoints/SKILL.md) for Flask Blueprint patterns.
- **New Pinia Stores**: Refer to [creating-pinia-stores/SKILL.md](file:///D:/ERP/POS/.agents/skills/creating-pinia-stores/SKILL.md) for state management patterns.
- **New Vue Components**: Refer to [creating-vue-components/SKILL.md](file:///D:/ERP/POS/.agents/skills/creating-vue-components/SKILL.md) for UI component patterns.
- **New Vue Views**: Refer to [creating-vue-views/SKILL.md](file:///D:/ERP/POS/.agents/skills/creating-vue-views/SKILL.md) for page-level view patterns.
- **New Backend Tests**: Refer to [writing-backend-tests/SKILL.md](file:///D:/ERP/POS/.agents/skills/writing-backend-tests/SKILL.md) for unittest patterns.

### Orchestration Skills
- **Full-Stack Features**: Refer to [adding-feature-end-to-end/SKILL.md](file:///D:/ERP/POS/.agents/skills/adding-feature-end-to-end/SKILL.md) for the complete model-to-UI implementation workflow.
