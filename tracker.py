import sqlite3
import hashlib
import os

DB = "expenses.db"

# ── Connection ────────────────────────────────────────────────────────────────
def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ── Schema setup ──────────────────────────────────────────────────────────────
def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fullname TEXT,
            email    TEXT
        )
    """)

    # Expenses table — now includes username column
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL DEFAULT 'admin',
            title    TEXT NOT NULL,
            amount   REAL NOT NULL,
            category TEXT,
            date     TEXT NOT NULL
        )
    """)

    # Income table (new)
    c.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title    TEXT NOT NULL,
            amount   REAL NOT NULL,
            category TEXT,
            date     TEXT NOT NULL
        )
    """)

    # Migrate old expenses that have no username (set to 'admin')
    c.execute("PRAGMA table_info(expenses)")
    cols = [row[1] for row in c.fetchall()]
    if "username" not in cols:
        c.execute("ALTER TABLE expenses ADD COLUMN username TEXT NOT NULL DEFAULT 'admin'")

    conn.commit()
    conn.close()

init_db()

# ── Helpers ───────────────────────────────────────────────────────────────────
def _hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ── User management ───────────────────────────────────────────────────────────
def seed_admin():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (username, password, fullname, email) VALUES (?,?,?,?)",
            ("admin", _hash("admin123"), "Administrator", "")
        )
        conn.commit()
    conn.close()

def verify_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?",
              (username, _hash(password)))
    row = c.fetchone()
    conn.close()
    return row is not None

def user_exists(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row is not None

def register_user(username, password, fullname="", email=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password, fullname, email) VALUES (?,?,?,?)",
        (username, _hash(password), fullname, email)
    )
    conn.commit()
    conn.close()

def change_password(username, new_password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE username=?",
              (_hash(new_password), username))
    conn.commit()
    conn.close()

# ── Expense CRUD (per-user) ───────────────────────────────────────────────────
def add_expense_record(username, title, amount, category, date):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO expenses (username, title, amount, category, date) VALUES (?,?,?,?,?)",
        (username, title, amount, category, date)
    )
    conn.commit()
    conn.close()

def view_expenses_records(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, title, amount, category, date FROM expenses WHERE username=? ORDER BY date DESC",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    return [tuple(r) for r in rows]

def get_expenses_for_month(username, month, year):
    conn = get_conn()
    c = conn.cursor()
    prefix = f"{year}-{month:02d}"
    c.execute(
        "SELECT id, title, amount, category, date FROM expenses WHERE username=? AND date LIKE ?",
        (username, f"{prefix}%")
    )
    rows = c.fetchall()
    conn.close()
    return [tuple(r) for r in rows]

def delete_expense_by_id(username, eid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=? AND username=?", (eid, username))
    conn.commit()
    conn.close()

def update_expense_amount(username, eid, amount):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE expenses SET amount=? WHERE id=? AND username=?", (amount, eid, username))
    conn.commit()
    conn.close()

def update_expense_title(username, eid, title):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE expenses SET title=? WHERE id=? AND username=?", (title, eid, username))
    conn.commit()
    conn.close()

def update_expense_category(username, eid, category):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE expenses SET category=? WHERE id=? AND username=?", (category, eid, username))
    conn.commit()
    conn.close()

# ── Income CRUD (new) ─────────────────────────────────────────────────────────
def add_income_record(username, title, amount, category, date):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO income (username, title, amount, category, date) VALUES (?,?,?,?,?)",
        (username, title, amount, category, date)
    )
    conn.commit()
    conn.close()

def view_income_records(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, title, amount, category, date FROM income WHERE username=? ORDER BY date DESC",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    return [tuple(r) for r in rows]

def get_income_for_month(username, month, year):
    conn = get_conn()
    c = conn.cursor()
    prefix = f"{year}-{month:02d}"
    c.execute(
        "SELECT id, title, amount, category, date FROM income WHERE username=? AND date LIKE ?",
        (username, f"{prefix}%")
    )
    rows = c.fetchall()
    conn.close()
    return [tuple(r) for r in rows]

def delete_income_by_id(username, iid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM income WHERE id=? AND username=?", (iid, username))
    conn.commit()
    conn.close()

# ── Stats (per-user) ──────────────────────────────────────────────────────────
def get_all_stats(username):
    # Use plain connection (no row_factory) so aggregate results
    # are real Python ints/floats, never sqlite3.Row objects
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT COUNT(*), COALESCE(SUM(amount),0) FROM expenses WHERE username=?", (username,))
    row = c.fetchone()
    exp_count = int(row[0])   if row[0] is not None else 0
    exp_total = float(row[1]) if row[1] is not None else 0.0

    c.execute("SELECT COALESCE(SUM(amount),0) FROM income WHERE username=?", (username,))
    row = c.fetchone()
    inc_total = float(row[0]) if row[0] is not None else 0.0

    conn.close()
    return {
        "count":   exp_count,
        "total":   exp_total,
        "income":  inc_total,
        "savings": inc_total - exp_total,
    }
