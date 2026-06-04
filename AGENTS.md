# Agent Instructions Router

Welcome, AI Agent! This file acts as the primary router for your operations in this codebase. Refer to the directory structures below to improve task outcomes, execute codebase commands, and maintain strict standards.

---

## 1. Project Context
- **Project Name**: ApexPOS
- **Core Structure**: Frontend is a Vue 3 SPA client in `frontend/`. Backend is a Flask API server in `backend/`.
- **Primary Rules**: Always review the code guidelines in the Rules folder:
  - [rules/coding_standards.md](file:///D:/ERP/POS/.agents/rules/coding_standards.md): Key principles on Flask App patterns, SQLAlchemy schemas, database update locks, and Pinia frontend store architecture.

---

## 2. Capabilities & Skills (How to perform tasks)
When instructed to run specific developer operations, view the corresponding files in the `.agents/skills/` directory using your file-viewing tools, making sure to flag them as skill execution files (set `IsSkillFile: true`):

- **Running Tests**: Refer to [skills/run_tests.md](file:///D:/ERP/POS/.agents/skills/run_tests.md) to check backend endpoint health.
- **Database Schema Upgrades**: Refer to [skills/db_migration.md](file:///D:/ERP/POS/.agents/skills/db_migration.md) to initialize or deploy Alembic DB migrations.
- **Compiling Frontend Assets**: Refer to [skills/build_frontend.md](file:///D:/ERP/POS/.agents/skills/build_frontend.md) to verify Vue component compilation.
