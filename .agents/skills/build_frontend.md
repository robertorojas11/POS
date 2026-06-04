# Skill: Build and Validate Frontend

Use this skill when you make modifications to Vue components, routes, or stores, and need to confirm code correctness and lint validation.

---

## Instructions

1. Navigate to the `frontend/` directory.
2. Install dependencies (if new packages were added to `package.json`):
   ```bash
   npm install
   ```
3. Run the development verification build:
   ```bash
   npm run build
   ```
4. Observe compile results:
   - Inspect Vite logs for syntax errors, import mismatches, or layout warnings.
   - If build fails, track down the error location and apply fixes.
   - If build succeeds (compiles into `dist/`), the static assets are ready for web servers.
