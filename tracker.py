import sqlite3
import os

DB_PATH = "expenses.db"

# ----------------------------------------------------
# Create tables if not exist
# ----------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        );
    """)

    conn.commit()
    conn.close()

# ----------------------------------------------------
# SEED ADMIN USER
# ----------------------------------------------------
def seed_admin():
    """Create default admin user if missing."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if admin already exists
    cur.execute("SELECT * FROM users WHERE username = 'admin'")
    exists = cur.fetchone()

    if not exists:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "admin123")
        )
        conn.commit()
        print("[OK] Default admin user created: admin / admin123")
    conn.close()

# ----------------------------------------------------
# VERIFY USER
# ----------------------------------------------------
def verify_user(username, password):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    res = cur.fetchone()
    conn.close()
    return res is not None

# ----------------------------------------------------
# CHANGE PASSWORD
# ----------------------------------------------------
def change_password(username, new_pw):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET password=? WHERE username=?", (new_pw, username))
    conn.commit()
    conn.close()

# ----------------------------------------------------
# EXPENSE CRUD
# ----------------------------------------------------
def add_expense_record(title, amount, cat, date):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO expenses (title, amount, category, date) VALUES (?, ?, ?, ?)",
                (title, amount, cat, date))
    conn.commit()
    conn.close()

def view_expenses_records():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses ORDER BY id DESC")
    res = cur.fetchall()
    conn.close()
    return res

def delete_expense_by_id(eid):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (eid,))
    conn.commit()
    conn.close()

def update_expense_amount(eid, amt):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE expenses SET amount=? WHERE id=?", (amt, eid))
    conn.commit()
    conn.close()

def update_expense_title(eid, title):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE expenses SET title=? WHERE id=?", (title, eid))
    conn.commit()
    conn.close()

def update_expense_category(eid, cat):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE expenses SET category=? WHERE id=?", (cat, eid))
    conn.commit()
    conn.close()

def get_all_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), SUM(amount) FROM expenses")
    res = cur.fetchone()
    conn.close()
    return {"count": res[0], "total": res[1] or 0}

def get_expenses_for_month(m, yr):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM expenses
        WHERE strftime('%m', date)=? AND strftime('%Y', date)=?
    """, (f"{m:02d}", str(yr)))
    res = cur.fetchall()
    conn.close()
    return res
def monthly_report_total(month, year=None):
    from datetime import date
    if year is None:
        year = date.today().year
    prefix = f'{year}-{int(month):02d}'
    import sqlite3, os
    db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'expenses.db')
    conn = sqlite3.connect(db)
    row = conn.execute('SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date LIKE ?', (prefix + '%',)).fetchone()
    conn.close()
    return row[0] if row else 0.0
