# API Contract Rules

Standards for the ApexPOS REST API design.

---

## 1. URL Structure
- Base: `/api/<resource>`
- Pattern: `/api/<blueprint-prefix>/<action-or-id>`
- Use kebab-case for multi-word paths (e.g., `/api/sales/shifts/active-all`)
- Use singular for blueprint names in code, but resource-appropriate in URLs.

## 2. HTTP Methods
| Action | Method | URL Pattern | Response |
|--------|--------|-------------|----------|
| List all | GET | `/api/resources` | `[entity.to_dict(), ...]` → 200 |
| Get one | GET | `/api/resources/<id>` | `entity.to_dict()` → 200 |
| Create | POST | `/api/resources` | `entity.to_dict()` → 201 |
| Update | PUT | `/api/resources/<id>` | `entity.to_dict()` → 200 |
| Delete | DELETE | `/api/resources/<id>` | `{"message": "..."}` → 200 |
| Action | POST | `/api/resources/<action>` | Varies → 200/201 |

## 3. Request Format
- Content-Type: `application/json`
- Body parsed with: `request.get_json() or {}`
- Query parameters for filtering: `request.args.get('param', default)`
- Custom headers: `X-Terminal-Id` for terminal identification.

## 4. Response Format

### Success
```json
// Single entity
{"id": 1, "name": "...", "created_at": "2026-01-01T00:00:00"}

// List of entities
[{"id": 1, ...}, {"id": 2, ...}]

// Action result
{"message": "Action completed successfully", "entity": {...}}
```

### Error
```json
{"error": "Human-readable error description"}
```

## 5. Status Codes
| Code | Usage |
|------|-------|
| 200 | Successful GET, PUT, DELETE, or action |
| 201 | Successful POST (resource created) |
| 400 | Validation error, missing fields, business rule violation |
| 401 | Missing or invalid JWT token |
| 403 | Valid token but insufficient role/permissions |
| 404 | Resource not found |
| 500 | Unexpected server error |

## 6. Authentication
- JWT Bearer token in `Authorization` header.
- Token issued at `POST /api/auth/login`.
- Identity is the user's integer ID as a string.
- Access token expires in 1 hour, refresh token in 7 days.

## 7. Authorization Roles
| Role | ID | Access Level |
|------|----|--------------|
| Admin | 1 | Full system access |
| Manager | 2 | Products, reports, shifts — no user/store management |
| Operator | 3 | POS register, own shift, coupon lookup |

## 8. Date Formats
- All dates returned as ISO 8601: `YYYY-MM-DDTHH:MM:SS`
- Date query parameters: `YYYY-MM-DD` format.
- All timestamps are UTC.

## 9. Numeric Precision
- Money fields: 2 decimal places (returned as float).
- Quantity fields: 3 decimal places (for weighted items).
