import os
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    import psycopg2
    import psycopg2.extras
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    USE_PG = True
else:
    import sqlite3
    USE_PG = False
    DB = "expenses.db"


def get_conn():
    if USE_PG:
        return psycopg2.connect(DATABASE_URL)
    else:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        return conn


def execute(query, params=(), fetchone=False, fetchall=False, commit=False):
    conn = get_conn()
    try:
        if USE_PG:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            query = query.replace("?", "%s")
        else:
            cur = conn.cursor()
        cur.execute(query, params)
        result = None
        if fetchone:
            row = cur.fetchone()
            result = dict(row) if row and USE_PG else row
        elif fetchall:
            rows = cur.fetchall()
            result = [dict(r) for r in rows] if USE_PG else rows
        if commit:
            conn.commit()
        return result
    finally:
        conn.close()


def init_db():
    if USE_PG:
        execute("""CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, fullname TEXT, email TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""", commit=True)
        execute("""CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY, username TEXT NOT NULL DEFAULT 'admin',
            title TEXT NOT NULL, amount REAL NOT NULL, category TEXT, date TEXT NOT NULL)""", commit=True)
        execute("""CREATE TABLE IF NOT EXISTS income (
            id SERIAL PRIMARY KEY, username TEXT NOT NULL,
            title TEXT NOT NULL, amount REAL NOT NULL, category TEXT, date TEXT NOT NULL)""", commit=True)
        execute("""CREATE TABLE IF NOT EXISTS budgets (
            id SERIAL PRIMARY KEY, username TEXT NOT NULL,
            category TEXT NOT NULL, amount REAL NOT NULL, month INT, year INT,
            UNIQUE(username, category, month, year))""", commit=True)
        execute("""CREATE TABLE IF NOT EXISTS goals (
            id SERIAL PRIMARY KEY, username TEXT NOT NULL,
            title TEXT NOT NULL, target REAL NOT NULL, saved REAL DEFAULT 0,
            deadline TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""", commit=True)
    else:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, fullname TEXT, email TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL DEFAULT 'admin',
            title TEXT NOT NULL, amount REAL NOT NULL, category TEXT, date TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL,
            title TEXT NOT NULL, amount REAL NOT NULL, category TEXT, date TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL,
            category TEXT NOT NULL, amount REAL NOT NULL, month INT, year INT,
            UNIQUE(username, category, month, year))""")
        c.execute("""CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL,
            title TEXT NOT NULL, target REAL NOT NULL, saved REAL DEFAULT 0,
            deadline TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("PRAGMA table_info(expenses)")
        cols = [row[1] for row in c.fetchall()]
        if "username" not in cols:
            c.execute("ALTER TABLE expenses ADD COLUMN username TEXT NOT NULL DEFAULT 'admin'")
        conn.commit()
        conn.close()

init_db()


def seed_admin():
    row = execute("SELECT id FROM users WHERE username=?", ("admin",), fetchone=True)
    if not row:
        execute("INSERT INTO users (username, password, fullname, email) VALUES (?,?,?,?)",
                ("admin", generate_password_hash("admin123"), "Administrator", ""), commit=True)


def verify_user(username, password):
    row = execute("SELECT password FROM users WHERE username=?", (username,), fetchone=True)
    if not row:
        return False
    stored = row["password"] if USE_PG else row[0]
    try:
        return check_password_hash(stored, password)
    except Exception:
        return stored == hashlib.sha256(password.encode()).hexdigest()


def user_exists(username):
    return execute("SELECT id FROM users WHERE username=?", (username,), fetchone=True) is not None


def register_user(username, password, fullname="", email=""):
    execute("INSERT INTO users (username, password, fullname, email) VALUES (?,?,?,?)",
            (username, generate_password_hash(password), fullname, email), commit=True)


def change_password(username, new_password):
    execute("UPDATE users SET password=? WHERE username=?",
            (generate_password_hash(new_password), username), commit=True)


def get_user_profile(username):
    row = execute("SELECT username, fullname, email, created_at FROM users WHERE username=?",
                  (username,), fetchone=True)
    if not row:
        return {}
    if USE_PG:
        return dict(row)
    return {"username": row[0], "fullname": row[1], "email": row[2], "created_at": row[3]}


def update_profile(username, fullname, email):
    execute("UPDATE users SET fullname=?, email=? WHERE username=?",
            (fullname, email, username), commit=True)


def _rows(rows):
    if not rows:
        return []
    if USE_PG:
        return [(r["id"], r["title"], r["amount"], r["category"], r["date"]) for r in rows]
    return [tuple(r) for r in rows]


# ── Expenses ──────────────────────────────────────────────────────────────────
def add_expense_record(username, title, amount, category, date):
    execute("INSERT INTO expenses (username, title, amount, category, date) VALUES (?,?,?,?,?)",
            (username, title, amount, category, date), commit=True)


def view_expenses_records(username):
    return _rows(execute(
        "SELECT id, title, amount, category, date FROM expenses WHERE username=? ORDER BY date DESC",
        (username,), fetchall=True))


def get_expenses_page(username, page=1, per_page=20):
    offset = (page - 1) * per_page
    rows = _rows(execute(
        "SELECT id, title, amount, category, date FROM expenses WHERE username=? ORDER BY date DESC LIMIT ? OFFSET ?",
        (username, per_page, offset), fetchall=True))
    total = execute("SELECT COUNT(*) as cnt FROM expenses WHERE username=?", (username,), fetchone=True)
    total_count = int(total["cnt"] if USE_PG else total[0])
    return rows, total_count


def get_expenses_for_month(username, month, year):
    return _rows(execute(
        "SELECT id, title, amount, category, date FROM expenses WHERE username=? AND date LIKE ?",
        (username, f"{year}-{month:02d}%"), fetchall=True))


def get_expenses_date_range(username, date_from, date_to):
    return _rows(execute(
        "SELECT id, title, amount, category, date FROM expenses WHERE username=? AND date >= ? AND date <= ? ORDER BY date DESC",
        (username, date_from, date_to), fetchall=True))


def delete_expense_by_id(username, eid):
    execute("DELETE FROM expenses WHERE id=? AND username=?", (eid, username), commit=True)


def delete_expenses_bulk(username, ids):
    for eid in ids:
        execute("DELETE FROM expenses WHERE id=? AND username=?", (int(eid), username), commit=True)


def update_expense_amount(username, eid, amount):
    execute("UPDATE expenses SET amount=? WHERE id=? AND username=?", (amount, eid, username), commit=True)


def update_expense_title(username, eid, title):
    execute("UPDATE expenses SET title=? WHERE id=? AND username=?", (title, eid, username), commit=True)


def update_expense_category(username, eid, category):
    execute("UPDATE expenses SET category=? WHERE id=? AND username=?", (category, eid, username), commit=True)


# ── Income ────────────────────────────────────────────────────────────────────
def add_income_record(username, title, amount, category, date):
    execute("INSERT INTO income (username, title, amount, category, date) VALUES (?,?,?,?,?)",
            (username, title, amount, category, date), commit=True)


def view_income_records(username):
    return _rows(execute(
        "SELECT id, title, amount, category, date FROM income WHERE username=? ORDER BY date DESC",
        (username,), fetchall=True))


def get_income_for_month(username, month, year):
    return _rows(execute(
        "SELECT id, title, amount, category, date FROM income WHERE username=? AND date LIKE ?",
        (username, f"{year}-{month:02d}%"), fetchall=True))


def delete_income_by_id(username, iid):
    execute("DELETE FROM income WHERE id=? AND username=?", (iid, username), commit=True)


def update_income_record(username, iid, title, amount, category):
    execute("UPDATE income SET title=?, amount=?, category=? WHERE id=? AND username=?",
            (title, amount, category, iid, username), commit=True)


# ── Budgets ───────────────────────────────────────────────────────────────────
def set_budget(username, category, amount, month, year):
    if USE_PG:
        execute("""INSERT INTO budgets (username, category, amount, month, year)
                   VALUES (?,?,?,?,?)
                   ON CONFLICT (username, category, month, year) DO UPDATE SET amount=?""",
                (username, category, amount, month, year, amount), commit=True)
    else:
        execute("""INSERT OR REPLACE INTO budgets (username, category, amount, month, year)
                   VALUES (?,?,?,?,?)""",
                (username, category, amount, month, year), commit=True)


def get_budgets(username, month, year):
    rows = execute(
        "SELECT category, amount FROM budgets WHERE username=? AND month=? AND year=?",
        (username, month, year), fetchall=True)
    if not rows:
        return {}
    if USE_PG:
        return {r["category"]: r["amount"] for r in rows}
    return {r[0]: r[1] for r in rows}


def delete_budget(username, category, month, year):
    execute("DELETE FROM budgets WHERE username=? AND category=? AND month=? AND year=?",
            (username, category, month, year), commit=True)


# ── Goals ─────────────────────────────────────────────────────────────────────
def add_goal(username, title, target, deadline):
    execute("INSERT INTO goals (username, title, target, saved, deadline) VALUES (?,?,?,0,?)",
            (username, title, target, deadline), commit=True)


def get_goals(username):
    rows = execute(
        "SELECT id, title, target, saved, deadline FROM goals WHERE username=? ORDER BY deadline ASC",
        (username,), fetchall=True)
    if not rows:
        return []
    if USE_PG:
        return [(r["id"], r["title"], r["target"], r["saved"], r["deadline"]) for r in rows]
    return [tuple(r) for r in rows]


def update_goal_saved(username, gid, amount):
    execute("UPDATE goals SET saved=? WHERE id=? AND username=?", (amount, gid, username), commit=True)


def delete_goal(username, gid):
    execute("DELETE FROM goals WHERE id=? AND username=?", (gid, username), commit=True)


# ── Stats ─────────────────────────────────────────────────────────────────────
def get_all_stats(username):
    exp = execute("SELECT COUNT(*) as cnt, COALESCE(SUM(amount),0) as total FROM expenses WHERE username=?",
                  (username,), fetchone=True)
    inc = execute("SELECT COALESCE(SUM(amount),0) as total FROM income WHERE username=?",
                  (username,), fetchone=True)
    if USE_PG:
        exp_count, exp_total, inc_total = int(exp["cnt"]), float(exp["total"]), float(inc["total"])
    else:
        exp_count, exp_total, inc_total = int(exp[0]), float(exp[1]), float(inc[0])
    return {"count": exp_count, "total": exp_total, "income": inc_total, "savings": inc_total - exp_total}


def get_top_expenses(username, month, year, limit=5):
    rows = execute(
        "SELECT title, amount, category FROM expenses WHERE username=? AND date LIKE ? ORDER BY amount DESC LIMIT ?",
        (username, f"{year}-{month:02d}%", limit), fetchall=True)
    if not rows:
        return []
    if USE_PG:
        return [(r["title"], r["amount"], r["category"]) for r in rows]
    return [tuple(r) for r in rows]


def get_monthly_comparison(username, month, year):
    prev_month = month - 1 if month > 1 else 12
    prev_year  = year if month > 1 else year - 1
    curr = execute("SELECT COALESCE(SUM(amount),0) as total FROM expenses WHERE username=? AND date LIKE ?",
                   (username, f"{year}-{month:02d}%"), fetchone=True)
    prev = execute("SELECT COALESCE(SUM(amount),0) as total FROM expenses WHERE username=? AND date LIKE ?",
                   (username, f"{prev_year}-{prev_month:02d}%"), fetchone=True)
    curr_total = float(curr["total"] if USE_PG else curr[0])
    prev_total = float(prev["total"] if USE_PG else prev[0])
    diff = curr_total - prev_total
    pct  = ((diff / prev_total) * 100) if prev_total > 0 else 0
    return {"current": curr_total, "previous": prev_total, "diff": diff, "pct": round(pct, 1)}
