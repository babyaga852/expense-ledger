# Expense Ledger — REST API

All endpoints require the user to be logged in (session cookie).

Base URL: `http://localhost:5000`

---

## Endpoints

### GET /api/expenses
List all expenses for the current user.

**Query params:**
| Param | Type | Description |
|-------|------|-------------|
| category | string | Filter by category (e.g. `Food`) |
| month | int | Filter by month (1-12) |
| year | int | Filter by year (e.g. 2026) |

**Response:**
```json
[
  { "id": 1, "title": "Coffee", "amount": 120.0, "category": "Food", "date": "2026-05-01" }
]
```

---

### POST /api/expenses
Add a new expense.

**Body:**
```json
{ "title": "Coffee", "amount": 120.0, "category": "Food", "date": "2026-05-01" }
```

**Response:** `201`
```json
{ "ok": true, "message": "Expense added" }
```

---

### PATCH /api/expenses/<id>
Update an expense.

**Body (all fields optional):**
```json
{ "title": "New title", "amount": 200.0, "category": "Transport" }
```

**Response:**
```json
{ "ok": true, "message": "Expense updated" }
```

---

### DELETE /api/expenses/<id>
Delete an expense.

**Response:**
```json
{ "ok": true, "message": "Expense 1 deleted" }
```

---

### GET /api/stats
Summary stats for the current user.

**Response:**
```json
{ "count": 42, "total": 15000.0, "income": 50000.0, "savings": 35000.0 }
```

---

### GET /api/expenses/summary?month=5&year=2026
Per-category breakdown for a month.

**Response:**
```json
{
  "month": 5, "year": 2026,
  "total": 5000.0,
  "by_category": { "Food": 2000.0, "Transport": 800.0 }
}
```

---

## Example with curl

```bash
# Login first to get session cookie
curl -c cookies.txt -X POST http://localhost:5000/login \
  -d "username=admin&password=yourpassword"

# Get all expenses
curl -b cookies.txt http://localhost:5000/api/expenses

# Add expense
curl -b cookies.txt -X POST http://localhost:5000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Lunch","amount":150,"category":"Food","date":"2026-05-10"}'

# Filter by category
curl -b cookies.txt "http://localhost:5000/api/expenses?category=Food"

# Monthly summary
curl -b cookies.txt "http://localhost:5000/api/expenses/summary?month=5&year=2026"
```
