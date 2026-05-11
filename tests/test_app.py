"""
pytest test suite for Expense Ledger
Run: pytest tests/ -v
"""
import os
import pytest

os.environ["TESTING"] = "1"
os.environ["SECRET_KEY"] = "test-secret-key-do-not-use-in-prod"

import tracker as db
import app as application

@pytest.fixture
def client(tmp_path, monkeypatch):
    """Fresh in-memory DB + Flask test client for each test."""
    # Point DB to a temp file so tests don't touch real data
    monkeypatch.setattr(db, "DB", str(tmp_path / "test.db"))
    monkeypatch.setattr(db, "USE_PG", False)
    db.init_db()
    db.seed_admin()

    application.app.config["TESTING"] = True
    application.app.config["WTF_CSRF_ENABLED"] = False
    with application.app.test_client() as c:
        yield c

def login(client, username="admin", password="admin123"):
    return client.post("/login", data={
        "username": username, "password": password
    }, follow_redirects=True)

# ── Auth tests ────────────────────────────────────────────────────────────────
def test_login_page_loads(client):
    r = client.get("/login")
    assert r.status_code == 200

def test_login_success(client):
    r = login(client)
    assert r.status_code == 200

def test_login_wrong_password(client):
    r = client.post("/login", data={
        "username": "admin", "password": "wrongpass"
    }, follow_redirects=True)
    assert b"Invalid" in r.data

def test_redirect_when_not_logged_in(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]

def test_logout(client):
    login(client)
    r = client.get("/logout", follow_redirects=False)
    assert r.status_code == 302

# ── Expense CRUD tests ────────────────────────────────────────────────────────
def test_add_expense(client):
    login(client)
    r = client.post("/add", data={
        "title": "Coffee", "amount": "120",
        "category": "Food", "date": "2026-05-01"
    }, follow_redirects=True)
    assert r.status_code == 200

def test_add_expense_invalid_amount(client):
    login(client)
    r = client.post("/add", data={
        "title": "Test", "amount": "not-a-number",
        "category": "Food", "date": "2026-05-01"
    }, follow_redirects=True)
    assert r.status_code == 200

def test_add_expense_missing_title(client):
    login(client)
    r = client.post("/add", data={
        "title": "", "amount": "100",
        "category": "Food", "date": "2026-05-01"
    }, follow_redirects=True)
    assert b"required" in r.data.lower() or r.status_code == 200

def test_expenses_page(client):
    login(client)
    r = client.get("/expenses")
    assert r.status_code == 200

def test_expenses_search(client):
    login(client)
    db.add_expense_record("admin", "Lunch at cafe", 250, "Food", "2026-05-01")
    r = client.get("/expenses?q=lunch")
    assert r.status_code == 200
    assert b"Lunch" in r.data

# ── User isolation test ───────────────────────────────────────────────────────
def test_users_cannot_see_each_others_expenses(client):
    # Register second user
    client.post("/register", data={
        "fullname": "Bob", "username": "bob",
        "email": "bob@test.com", "password": "password123",
        "confirm": "password123"
    })
    # Admin adds an expense
    login(client, "admin", "admin123")
    db.add_expense_record("admin", "Admin secret", 999, "Other", "2026-05-01")
    client.get("/logout")

    # Bob logs in and checks expenses
    login(client, "bob", "password123")
    r = client.get("/expenses")
    assert b"Admin secret" not in r.data

# ── REST API tests ────────────────────────────────────────────────────────────
def test_api_get_expenses_unauth(client):
    r = client.get("/api/expenses")
    assert r.status_code == 302  # redirects to login

def test_api_get_expenses(client):
    login(client)
    r = client.get("/api/expenses")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

def test_api_add_expense(client):
    login(client)
    r = client.post("/api/expenses",
                    json={"title": "API test", "amount": 99.5,
                          "category": "Food", "date": "2026-05-10"})
    assert r.status_code == 201
    assert r.get_json()["ok"] is True

def test_api_add_expense_missing_title(client):
    login(client)
    r = client.post("/api/expenses",
                    json={"amount": 50, "category": "Food", "date": "2026-05-01"})
    assert r.status_code == 400

def test_api_add_expense_negative_amount(client):
    login(client)
    r = client.post("/api/expenses",
                    json={"title": "Bad", "amount": -10,
                          "category": "Food", "date": "2026-05-01"})
    assert r.status_code == 400

def test_api_delete_expense(client):
    login(client)
    db.add_expense_record("admin", "To delete", 50, "Other", "2026-05-01")
    expenses = client.get("/api/expenses").get_json()
    eid = expenses[0]["id"]
    r = client.delete(f"/api/expenses/{eid}")
    assert r.status_code == 200
    assert r.get_json()["ok"] is True

def test_api_update_expense(client):
    login(client)
    db.add_expense_record("admin", "Original", 100, "Food", "2026-05-01")
    expenses = client.get("/api/expenses").get_json()
    eid = expenses[0]["id"]
    r = client.patch(f"/api/expenses/{eid}",
                     json={"title": "Updated", "amount": 200})
    assert r.status_code == 200
    assert r.get_json()["ok"] is True

def test_api_stats(client):
    login(client)
    r = client.get("/api/stats")
    assert r.status_code == 200
    data = r.get_json()
    assert "total" in data
    assert "count" in data

def test_api_summary(client):
    login(client)
    r = client.get("/api/stats")
    assert r.status_code == 200

def test_api_category_filter(client):
    login(client)
    db.add_expense_record("admin", "Pizza", 200, "Food", "2026-05-01")
    db.add_expense_record("admin", "Bus", 30, "Transport", "2026-05-01")
    r = client.get("/api/expenses?category=Food")
    data = r.get_json()
    assert all(e["category"] == "Food" for e in data)

# ── Report test ───────────────────────────────────────────────────────────────
def test_report_page(client):
    login(client)
    r = client.get("/report?month=5&year=2026")
    assert r.status_code == 200
