# Skill: Database Migrations with Flask-Migrate

Use this skill when database models are modified and SQL schemas must be generated/updated in PostgreSQL.

---

## Instructions

1. Ensure the Python virtual environment is activated:
   - On Windows: `backend\venv\Scripts\activate`
   - On Linux/macOS: `source backend/venv/bin/activate`
2. Navigate to the `backend/` directory.
3. If this is the **first time** setting up migrations, run:
   ```bash
   flask db init
   ```
   *(This creates the `migrations/` folder structure)*.
4. Auto-generate a migration script comparing models to the active DB schema:
   ```bash
   flask db migrate -m "Description of changes"
   ```
5. Inspect the generated migration script in `backend/migrations/versions/` to verify correctness.
6. Apply the migration schema upgrades to the PostgreSQL instance:
   ```bash
   flask db upgrade
   ```
7. Verify that database tables match the updated model files.
