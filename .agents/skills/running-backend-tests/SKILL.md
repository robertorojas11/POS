---
name: running-backend-tests
description: Runs backend unit and integration tests to verify code changes. Use when testing the Python/Flask backend, running test suites, or validating backend modifications.
---

# Run Backend Unit Tests

## When to use this skill
- Verifying backend Python/Flask code changes.
- Running unit or integration test suites.
- Checking backend behavior or diagnosing failures after a bug fix.

## Workflow
1. [ ] **Validate Prerequisites**: Ensure the `backend/` directory and Python virtual environment exist.
2. [ ] **Prepare Environment**: Determine the shell type to configure the `FLASK_CONFIG` environment variable.
3. [ ] **Execute Tests**: Activate the virtual environment and run the test suite with the working directory set to `backend/`.
4. [ ] **Analyze Output**: Check the results. If errors occur, isolate the failures or tracebacks and modify the target module.

## Instructions

### 1. Prerequisites Check
Before running any tests, verify the presence of the Python virtual environment folder:
* Windows: `backend/venv/Scripts/`
* Linux/macOS: `backend/venv/bin/`

### 2. Environment Activation & Variables
Do not change directories (`cd`). Set the command's working directory (`Cwd`) to the `backend/` directory and execute the appropriate activation command for the shell:

* **Windows PowerShell**:
  ```powershell
  . venv/Scripts/Activate.ps1; $env:FLASK_CONFIG="testing"; python -m unittest discover -s tests -p "test_*.py" -v
  ```
* **Windows CMD**:
  ```cmd
  call venv\Scripts\activate.bat && set FLASK_CONFIG=testing && python -m unittest discover -s tests -p "test_*.py" -v
  ```
* **Linux/macOS / Bash**:
  ```bash
  source venv/bin/activate && export FLASK_CONFIG="testing" && python -m unittest discover -s tests -p "test_*.py" -v
  ```

### 3. Running a Single Test File
To run tests for a specific domain:
```bash
python -m unittest tests.test_auth -v
python -m unittest tests.test_shift -v
```

### 4. Testing Configuration
Tests use `create_app('testing')` which loads `TestingConfig` from `backend/app/config.py`:
- **Database**: `postgresql://postgres:postgres@localhost:5432/pos_test_db`
- **Redis**: `redis://localhost:6379/1` (separate DB index from development)

Ensure PostgreSQL and Redis are running before executing tests.

### 5. Current Test Files
| File | Domain | Key Tests |
|------|--------|-----------|
| `tests/test_auth.py` | Authentication | Registration, login, employee CRUD, audit trail |
| `tests/test_shift.py` | Shifts & Sales | Shift lifecycle, checkout, discounts, UOM, SSE, terminal cache |

### 6. Error Handling
- If the unittest discovery fails or if you encounter import issues, check the dependencies by running `pip list` within the activated environment.
- For help with unittest command-line arguments, run:
  ```bash
  python -m unittest --help
  ```
