import sqlite3
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_DB   = os.path.join(_HERE, "expenses.db")


def _connect():
    conn = sqlite3.connect(_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            title    TEXT    NOT NULL,
            amount   REAL    NOT NULL,
            category TEXT    NOT NULL,
            date     TEXT    NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            fullname TEXT    DEFAULT '',
            email    TEXT    DEFAULT ''
        )
    """)
    conn.commit()
    return conn


# ── Seed default admin if no users exist ──────────────────────────────────────
def seed_admin():
    import hashlib
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
        if row[0] == 0:
            pw = hashlib.sha256("admin123".encode()).hexdigest()
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                         ("admin", pw))
            conn.commit()


# ── Auth ──────────────────────────────────────────────────────────────────────
def verify_user(username, password):
    import hashlib
    pw = hashlib.sha256(password.encode()).hexdigest()
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, pw)
        ).fetchone()
    return row is not None


def change_password(username, new_password):
    import hashlib
    pw = hashlib.sha256(new_password.encode()).hexdigest()
    with _connect() as conn:
        conn.execute("UPDATE users SET password=? WHERE username=?", (pw, username))
        conn.commit()


# ── Expenses CRUD ─────────────────────────────────────────────────────────────
def add_expense_record(title, amount, category, date_s):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO expenses (title, amount, category, date) VALUES (?,?,?,?)",
            (title, float(amount), category, date_s)
        )
        conn.commit()


def view_expenses_records():
    with _connect() as conn:
        return conn.execute(
            "SELECT id, title, amount, category, date FROM expenses ORDER BY date DESC, id DESC"
        ).fetchall()


def delete_expense_by_id(eid):
    with _connect() as conn:
        cur = conn.execute("DELETE FROM expenses WHERE id=?", (eid,))
        conn.commit()
        return cur.rowcount > 0


def update_expense_amount(eid, new_amount):
    with _connect() as conn:
        cur = conn.execute("UPDATE expenses SET amount=? WHERE id=?",
                           (float(new_amount), eid))
        conn.commit()
        return cur.rowcount > 0


def update_expense_title(eid, new_title):
    with _connect() as conn:
        conn.execute("UPDATE expenses SET title=? WHERE id=?", (new_title, eid))
        conn.commit()


def update_expense_category(eid, new_cat):
    with _connect() as conn:
        conn.execute("UPDATE expenses SET category=? WHERE id=?", (new_cat, eid))
        conn.commit()


def monthly_report_total(month, year=None):
    from datetime import date
    if year is None:
        year = date.today().year
    prefix = f"{year}-{int(month):02d}"
    with _connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date LIKE ?",
            (prefix + "%",)
        ).fetchone()
    return row[0] if row else 0.0


def get_expenses_for_month(month, year):
    prefix = f"{int(year)}-{int(month):02d}"
    with _connect() as conn:
        return conn.execute(
            "SELECT id, title, amount, category, date FROM expenses WHERE date LIKE ? ORDER BY date DESC",
            (prefix + "%",)
        ).fetchall()


def get_all_stats():
    with _connect() as conn:
        total = conn.execute("SELECT COALESCE(SUM(amount),0) FROM expenses").fetchone()[0]
        count = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
        cats  = conn.execute(
            "SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC"
        ).fetchall()
    return {"total": total, "count": count, "categories": cats}


def user_exists(username):
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE username=?", (username,)
        ).fetchone()
    return row is not None


def register_user(username, password, fullname="", email=""):
    import hashlib
    pw = hashlib.sha256(password.encode()).hexdigest()
    with _connect() as conn:
        try:
            conn.execute("ALTER TABLE users ADD COLUMN fullname TEXT DEFAULT ''")
        except: pass
        try:
            conn.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
        except: pass
        conn.execute(
            "INSERT INTO users (username, password, fullname, email) VALUES (?,?,?,?)",
            (username, pw, fullname, email)
        )
        conn.commit()