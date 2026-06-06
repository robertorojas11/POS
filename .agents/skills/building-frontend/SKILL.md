---
name: building-frontend
description: Builds and validates the ApexPOS Vue 3 frontend. Use when verifying Vue component compilation, checking for build errors, or preparing production assets.
---

# Build and Validate Frontend

## When to use this skill
- Verifying that Vue components, routes, or stores compile correctly after changes.
- Checking for import errors, missing dependencies, or template syntax issues.
- Preparing production-ready static assets.

## Workflow
1. [ ] **Check dependencies**: Install any new packages if `package.json` was modified.
2. [ ] **Run build**: Execute the Vite production build.
3. [ ] **Analyze output**: Check for compilation errors and warnings.
4. [ ] **Fix issues**: Track down and resolve any errors.

## Instructions

### 1. Install Dependencies
If new packages were added to `package.json`, run the install command first. Set `Cwd` to `frontend/`:
```bash
npm install
```

### 2. Run Build Verification
Execute the production build to check for compilation errors:
```bash
npm run build
```

### 3. Expected Output
A successful build produces:
```
vite v8.x.x building for production...
✓ N modules transformed.
dist/index.html
dist/assets/index-XXXXX.css    XX.XX kB │ gzip: XX.XX kB
dist/assets/index-XXXXX.js     XXX.XX kB │ gzip: XX.XX kB
✓ built in Xs
```

### 4. Common Error Types

#### Import Errors
```
ERROR: Could not resolve "@/store/nonexistent"
```
**Fix**: Verify the import path matches an existing file under `frontend/src/`.

#### Template Syntax Errors
```
ERROR: Unexpected token in template
```
**Fix**: Check the `.vue` file's `<template>` section for unclosed tags or invalid syntax.

#### Missing Dependencies
```
ERROR: Cannot find module 'some-package'
```
**Fix**: Run `npm install some-package` or check `package.json`.

### 5. Current Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| `vue` | ^3.5.34 | Core framework |
| `vue-router` | ^5.1.0 | SPA routing |
| `pinia` | ^3.0.4 | State management |
| `axios` | ^1.17.0 | HTTP client |
| `lucide-vue-next` | ^1.0.0 | Icon library |

### 6. Dev Server (Alternative)
To run the development server with hot reload for live testing:
```bash
npm run dev
```
The dev server starts on `http://localhost:5173` with Vite proxy forwarding `/api` to the Flask backend.

> **Note**: The Vite proxy in `vite.config.js` targets `http://backend:5000` (Docker). For local development without Docker, ensure the proxy target is set to `http://localhost:5000`.
