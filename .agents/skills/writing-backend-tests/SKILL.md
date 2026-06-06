---
name: writing-backend-tests
description: Writes new backend unit and integration tests for the ApexPOS Flask API. Use when implementing new test cases, verifying endpoint behavior, or expanding test coverage.
---

# Writing Backend Tests

## When to use this skill
- Writing tests for new or modified API endpoints.
- Adding regression tests after a bug fix.
- Expanding test coverage for existing features.

## Workflow
1. [ ] **Identify test scope**: Determine which endpoint(s) or service(s) to test.
2. [ ] **Create/update test file** in `backend/tests/`.
3. [ ] **Write setUp fixtures** following the established pattern.
4. [ ] **Write test methods** covering success, validation, and authorization cases.
5. [ ] **Run tests** using the `running-backend-tests` skill.

## Instructions

### 1. File Naming & Structure
- Test files go in `backend/tests/`.
- Naming: `test_<domain>.py` (e.g., `test_auth.py`, `test_shift.py`, `test_products.py`).
- Each file contains one `unittest.TestCase` subclass.

### 2. Test Class Template
```python
import unittest
import json
from app import create_app, db
from app.models.user import User, UserType
# Import other models as needed

class YourDomainTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        # Clean tables in FK-dependency order (children first)
        db.session.execute(db.delete(User))
        db.session.execute(db.delete(UserType))
        db.session.commit()
        
        # Seed required user types (ALWAYS needed)
        for ut_id, ut_name in [(1, "Admin"), (2, "Manager"), (3, "Operator")]:
            if not db.session.get(UserType, ut_id):
                db.session.add(UserType(id=ut_id, name=ut_name))
        db.session.commit()
        
        # Create test user and authenticate
        self.user = User(username="testuser", email="test@example.com", user_type_id=1)
        self.user.set_password("testpass")
        db.session.add(self.user)
        db.session.commit()
        
        payload = {"username": "testuser", "password": "testpass"}
        response = self.client.post('/api/auth/login',
            data=json.dumps(payload), content_type='application/json')
        data = json.loads(response.data.decode('utf-8'))
        self.headers = {'Authorization': f'Bearer {data["access_token"]}'}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_example_success(self):
        response = self.client.get('/api/endpoint', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        # Assert on response shape and values

    def test_example_validation_error(self):
        response = self.client.post('/api/endpoint',
            headers=self.headers,
            data=json.dumps({}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('error', data)

    def test_example_unauthorized(self):
        # Test without auth headers
        response = self.client.get('/api/endpoint')
        self.assertEqual(response.status_code, 401)

    def test_example_forbidden(self):
        # Create operator user and test admin-only endpoint
        op = User(username="operator1", email="op@example.com", user_type_id=3)
        op.set_password("oppass")
        db.session.add(op)
        db.session.commit()
        login = self.client.post('/api/auth/login',
            data=json.dumps({"username": "operator1", "password": "oppass"}),
            content_type='application/json')
        op_headers = {'Authorization': f'Bearer {json.loads(login.data.decode("utf-8"))["access_token"]}'}
        response = self.client.get('/api/admin-endpoint', headers=op_headers)
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()
```

### 3. Test Categories to Cover
For each endpoint, write tests for:
- **Happy path**: Valid input returns expected response.
- **Validation**: Missing/invalid fields return 400.
- **Auth**: No token returns 401.
- **Authorization**: Wrong role returns 403.
- **Uniqueness**: Duplicate entries return 400.
- **Not found**: Invalid IDs return 404.
- **Audit trail**: Verify `created_by_id` / `updated_by_id` are set.

### 4. Existing Test Files
| File | TestCase | Tests |
|------|----------|-------|
| `test_auth.py` | `AuthTestCase` | Registration, login, employee CRUD + audit trail |
| `test_shift.py` | `ShiftTestCase` | Shift lifecycle, checkout, discounts, UOM, SSE, terminal cache |

### 5. Testing Config
Tests use `create_app('testing')` which loads `TestingConfig`:
- Database: `postgresql://postgres:postgres@localhost:5432/pos_test_db`
- Redis: `redis://localhost:6379/1` (separate DB index)

## Why This Skill Exists
- **Protects**: Consistent test setup/teardown, proper app context management, auth fixture reuse.
- **Prevents**: Tests leaking state, missing UserType seeds, forgotten auth headers.
- **Evolution**: Consider adding pytest fixtures and conftest.py as the test suite grows.
