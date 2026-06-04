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
  . venv/Scripts/Activate.ps1
  $env:FLASK_CONFIG="testing"
  ```
* **Windows CMD**:
  ```cmd
  call venv\Scripts\activate.bat
  set FLASK_CONFIG=testing
  ```
* **Linux/macOS / Bash**:
  ```bash
  source venv/bin/activate
  export FLASK_CONFIG="testing"
  ```

### 3. Run the Tests
With the virtual environment activated and `FLASK_CONFIG` set, execute the Python unittest command inside the `backend/` directory:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### 4. Error Handling
- If the unittest discovery fails or if you encounter import issues, check the dependencies by running `pip list` within the activated environment.
- For help with unittest command-line arguments, run:
  ```bash
  python -m unittest --help
  ```
