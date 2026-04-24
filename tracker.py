import os
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

# ── Database setup ─────────────────────────────────────────────────────────────
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
            password TEXT NOT NULL, fullname TEXT, email TEXT)""", commit=True)
        execute("""CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY, username TEXT NOT NULL DEFAULT 'admin',
            title TEXT NOT NULL, amount REAL NOT NULL, category TEXT, date TEXT NOT NULL)""", commit=True)
        execute("""CREATE TABLE IF NOT EXISTS income (
            id SERIAL PRIMARY KEY, username TEXT NOT NULL,
            title TEXT NOT NULL, amount REAL NOT NULL, category TEXT, date TEXT NOT NULL)""", commit=True)
    else:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, fullname TEXT, email TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL DEFAULT 'admin',
            title TEXT NOT NULL, amount REAL NOT NULL, category TEXT, date TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL,
            title TEXT NOT NULL, amount REAL NOT NULL, category TEXT, date TEXT NOT NULL)""")
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


def add_expense_record(username, title, amount, category, date):
    execute("INSERT INTO expenses (username, title, amount, category, date) VALUES (?,?,?,?,?)",
            (username, title, amount, category, date), commit=True)


def _rows(rows):
    if not rows:
        return []
    if USE_PG:
        return [(r["id"], r["title"], r["amount"], r["category"], r["date"]) for r in rows]
    return [tuple(r) for r in rows]


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


def delete_expense_by_id(username, eid):
    execute("DELETE FROM expenses WHERE id=? AND username=?", (eid, username), commit=True)


def update_expense_amount(username, eid, amount):
    execute("UPDATE expenses SET amount=? WHERE id=? AND username=?", (amount, eid, username), commit=True)


def update_expense_title(username, eid, title):
    execute("UPDATE expenses SET title=? WHERE id=? AND username=?", (title, eid, username), commit=True)


def update_expense_category(username, eid, category):
    execute("UPDATE expenses SET category=? WHERE id=? AND username=?", (category, eid, username), commit=True)


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


# ── User settings (currency, onboarding) ─────────────────────────────────────
def _init_settings():
    if USE_PG:
        execute("""CREATE TABLE IF NOT EXISTS user_settings (
            username TEXT PRIMARY KEY,
            currency TEXT DEFAULT 'INR',
            currency_symbol TEXT DEFAULT '₹',
            onboarded INTEGER DEFAULT 0)""", commit=True)
    else:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS user_settings (
            username TEXT PRIMARY KEY,
            currency TEXT DEFAULT 'INR',
            currency_symbol TEXT DEFAULT '₹',
            onboarded INTEGER DEFAULT 0)""")
        conn.commit()
        conn.close()

_init_settings()

CURRENCIES = {
    'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£',
    'JPY': '¥', 'AED': 'د.إ', 'SGD': 'S$', 'CAD': 'C$'
}

def get_user_settings(username):
    row = execute("SELECT currency, currency_symbol, onboarded FROM user_settings WHERE username=?",
                  (username,), fetchone=True)
    if not row:
        execute("INSERT INTO user_settings (username, currency, currency_symbol, onboarded) VALUES (?,?,?,0)",
                (username, 'INR', '₹'), commit=True)
        return {'currency': 'INR', 'symbol': '₹', 'onboarded': 0}
    if USE_PG:
        return {'currency': row['currency'], 'symbol': row['currency_symbol'], 'onboarded': row['onboarded']}
    return {'currency': row[0], 'symbol': row[1], 'onboarded': row[2]}

def set_currency(username, currency):
    symbol = CURRENCIES.get(currency, '₹')
    execute("""INSERT INTO user_settings (username, currency, currency_symbol, onboarded)
               VALUES (?,?,?,1) ON CONFLICT(username) DO UPDATE SET currency=?, currency_symbol=?""" if USE_PG else
            """INSERT OR REPLACE INTO user_settings (username, currency, currency_symbol, onboarded)
               VALUES (?,?,?,(SELECT onboarded FROM user_settings WHERE username=?))""",
            (username, currency, symbol, currency, symbol) if USE_PG else
            (username, currency, symbol, username), commit=True)

def complete_onboarding(username):
    execute("""INSERT INTO user_settings (username, currency, currency_symbol, onboarded)
               VALUES (?,?,?,1) ON CONFLICT(username) DO UPDATE SET onboarded=1""" if USE_PG else
            """INSERT OR REPLACE INTO user_settings (username, currency, currency_symbol, onboarded)
               VALUES (?, COALESCE((SELECT currency FROM user_settings WHERE username=?),'INR'),
                          COALESCE((SELECT currency_symbol FROM user_settings WHERE username=?),'₹'), 1)""",
            (username, username, username) if not USE_PG else (username, 'INR', '₹'),
            commit=True)

def get_notifications(username, month, year):
    notifs = []
    # Budget alerts
    budgets = get_budgets(username, month, year)
    expenses = get_expenses_for_month(username, month, year)
    spent_by_cat = {}
    for r in expenses:
        spent_by_cat[r[3]] = spent_by_cat.get(r[3], 0) + r[2]
    for cat, limit in budgets.items():
        spent = spent_by_cat.get(cat, 0)
        if spent >= limit:
            notifs.append({'type': 'danger', 'msg': f'{cat} budget exceeded! Spent {spent:.0f} of {limit:.0f}'})
        elif spent >= limit * 0.8:
            notifs.append({'type': 'warning', 'msg': f'{cat} at {int(spent/limit*100)}% of budget'})
    # Goal completions
    goals = get_goals(username)
    for g in goals:
        if g[2] > 0 and g[3] >= g[2]:
            notifs.append({'type': 'success', 'msg': f'Goal "{g[1]}" completed! 🎉'})
    return notifs
