import os
import io
from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify, send_file)
from datetime import datetime, date
import tracker as db

app = Flask(__name__)

# ── FIX #1: Secret key from environment variable, never hardcoded ─────────────
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

db.seed_admin()

EXPENSE_CATS = ["Food", "Transport", "Shopping", "Bills",
                "Health", "Entertainment", "Education", "Other"]

INCOME_CATS = ["Salary", "Freelance", "Business", "Investment",
               "Gift", "Rental", "Other"]

# ── Auth guard ────────────────────────────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if db.verify_user(username, password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", error=error, success=None, mode="login")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    success = None
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm", "")

        if not fullname or not username or not password:
            error = "Full name, username and password are required."
        elif len(username) < 3:
            error = "Username must be at least 3 characters."
        elif " " in username:
            error = "Username cannot contain spaces."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."
        elif db.user_exists(username):
            error = f"Username '{username}' is already taken."
        else:
            db.register_user(username, password, fullname, email)
            success = f"Account created! Welcome, {fullname}. Please sign in."
            return render_template("login.html", error=None, success=success, mode="login")

    return render_template("login.html", error=error, success=success, mode="register")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/change-password", methods=["POST"])
@login_required
def change_password():
    new_pw  = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")
    if new_pw != confirm:
        return jsonify({"ok": False, "msg": "Passwords do not match."})
    if len(new_pw) < 6:
        return jsonify({"ok": False, "msg": "Password must be at least 6 characters."})
    db.change_password(session["user"], new_pw)
    return jsonify({"ok": True, "msg": "Password changed successfully."})

# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def dashboard():
    user  = session["user"]
    # ── FIX #2: all DB calls now pass username ────────────────────────────────
    rows  = db.view_expenses_records(user)
    stats = db.get_all_stats(user)
    today = date.today()

    monthly_exp = sum(r[2] for r in rows
                      if str(r[4]).startswith(f"{today.year}-{today.month:02d}"))

    income_rows   = db.view_income_records(user)
    monthly_inc   = sum(r[2] for r in income_rows
                        if str(r[4]).startswith(f"{today.year}-{today.month:02d}"))

    # ── FIX #4: build chart data for dashboard ────────────────────────────────
    # Category breakdown (pie chart)
    cat_totals = {}
    for r in rows:
        cat_totals[r[3]] = cat_totals.get(r[3], 0) + r[2]

    # Last 6 months trend (bar chart)
    from datetime import datetime as dt
    import calendar
    monthly_trend = []
    for i in range(5, -1, -1):
        mo = (today.month - i - 1) % 12 + 1
        yr = today.year - ((today.month - i - 1) // 12)
        label = dt(yr, mo, 1).strftime("%b %Y")
        exp_sum = sum(r[2] for r in rows if str(r[4]).startswith(f"{yr}-{mo:02d}"))
        inc_sum = sum(r[2] for r in income_rows if str(r[4]).startswith(f"{yr}-{mo:02d}"))
        monthly_trend.append({"label": label, "expense": exp_sum, "income": inc_sum})

    recent = rows[:8]

    return render_template("index.html",
        page="dashboard", stats=stats, recent=recent,
        monthly_exp=monthly_exp, monthly_inc=monthly_inc,
        today=today, cats=EXPENSE_CATS, user=user,
        cat_totals=cat_totals, monthly_trend=monthly_trend)

# ── Expenses ──────────────────────────────────────────────────────────────────
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    user  = session["user"]
    msg   = None
    error = None
    if request.method == "POST":
        title    = request.form.get("title", "").strip()
        amount_s = request.form.get("amount", "").strip()
        category = request.form.get("category", "")
        date_s   = request.form.get("date", "")
        try:
            amount = float(amount_s)
            datetime.strptime(date_s, "%Y-%m-%d")
            # ── FIX #2: pass username to add ─────────────────────────────────
            db.add_expense_record(user, title, amount, category, date_s)
            msg = f"Added ₹{amount:,.2f} — {title}"
        except ValueError as e:
            error = str(e)

    return render_template("index.html", page="add", cats=EXPENSE_CATS,
                           msg=msg, error=error,
                           today=date.today(), user=user)

@app.route("/expenses")
@login_required
def expenses():
    user = session["user"]
    q    = request.args.get("q", "").lower()
    rows = db.view_expenses_records(user)   # ── FIX #2
    if q:
        rows = [r for r in rows
                if q in r[1].lower() or q in r[3].lower() or q in str(r[4])]
    return render_template("index.html", page="expenses",
                           rows=rows, q=q, cats=EXPENSE_CATS,
                           today=date.today(), user=user)

@app.route("/delete/<int:eid>", methods=["POST"])
@login_required
def delete(eid):
    db.delete_expense_by_id(session["user"], eid)   # ── FIX #2
    return redirect(url_for("expenses"))

@app.route("/update/<int:eid>", methods=["POST"])
@login_required
def update(eid):
    user  = session["user"]
    amt_s = request.form.get("amount", "").strip()
    title = request.form.get("title", "").strip()
    cat   = request.form.get("category", "").strip()
    if amt_s:
        try: db.update_expense_amount(user, eid, float(amt_s))
        except: pass
    if title:
        db.update_expense_title(user, eid, title)
    if cat and cat != "(keep)":
        db.update_expense_category(user, eid, cat)
    return redirect(url_for("expenses"))

# ── FIX #3: Income routes (new) ───────────────────────────────────────────────
@app.route("/income")
@login_required
def income():
    user = session["user"]
    rows = db.view_income_records(user)
    return render_template("index.html", page="income",
                           rows=rows, cats=INCOME_CATS,
                           today=date.today(), user=user)

@app.route("/income/add", methods=["POST"])
@login_required
def add_income():
    user     = session["user"]
    title    = request.form.get("title", "").strip()
    amount_s = request.form.get("amount", "").strip()
    category = request.form.get("category", "")
    date_s   = request.form.get("date", "")
    try:
        amount = float(amount_s)
        datetime.strptime(date_s, "%Y-%m-%d")
        db.add_income_record(user, title, amount, category, date_s)
    except ValueError:
        pass
    return redirect(url_for("income"))

@app.route("/income/delete/<int:iid>", methods=["POST"])
@login_required
def delete_income(iid):
    db.delete_income_by_id(session["user"], iid)
    return redirect(url_for("income"))

# ── Report ────────────────────────────────────────────────────────────────────
@app.route("/report")
@login_required
def report():
    user  = session["user"]
    today = date.today()
    m     = int(request.args.get("month", today.month))
    yr    = int(request.args.get("year",  today.year))

    rows     = db.get_expenses_for_month(user, m, yr)   # ── FIX #2
    inc_rows = db.get_income_for_month(user, m, yr)

    total     = sum(r[2] for r in rows)
    inc_total = sum(r[2] for r in inc_rows)

    cat_t = {}
    for r in rows:
        cat_t[r[3]] = cat_t.get(r[3], 0) + r[2]
    cat_data = sorted(cat_t.items(), key=lambda x: -x[1])

    month_name = datetime(2000, m, 1).strftime("%B")

    return render_template("index.html", page="report",
        rows=rows, total=total, cat_data=cat_data,
        inc_rows=inc_rows, inc_total=inc_total,
        month=m, year=yr, month_name=month_name,
        cats=EXPENSE_CATS, today=today, user=user)

# ── Exports ───────────────────────────────────────────────────────────────────
@app.route("/export/excel")
@login_required
def export_excel():
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
    except ImportError:
        return "Install openpyxl: pip install openpyxl", 500

    user = session["user"]
    rows = db.view_expenses_records(user)
    wb   = openpyxl.Workbook()
    ws   = wb.active
    ws.title = "Expenses"

    hdr_font = Font(bold=True, color="FFFFFF", size=11)
    hdr_fill = PatternFill("solid", fgColor="1a2035")
    headers  = ["ID", "Title", "Amount (₹)", "Category", "Date"]
    col_w    = [8, 35, 18, 18, 15]

    for i, (h, w) in enumerate(zip(headers, col_w), 1):
        c = ws.cell(row=1, column=i, value=h)
        c.font = hdr_font; c.fill = hdr_fill
        c.alignment = Alignment(horizontal="center")
        ws.column_dimensions[c.column_letter].width = w

    for ri, row in enumerate(rows, 2):
        for ci, val in enumerate(row, 1):
            c = ws.cell(row=ri, column=ci, value=val)
            c.alignment = Alignment(horizontal="center" if ci != 2 else "left")
        ws.cell(row=ri, column=3).number_format = "#,##0.00"

    last = len(rows) + 2
    ws.cell(row=last, column=2, value="TOTAL").font = Font(bold=True)
    ws.cell(row=last, column=3, value=sum(r[2] for r in rows)).font = Font(bold=True)
    ws.cell(row=last, column=3).number_format = "#,##0.00"

    buf = io.BytesIO()
    wb.save(buf); buf.seek(0)
    return send_file(buf, as_attachment=True,
                     download_name=f"expenses_{date.today()}.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.route("/export/pdf")
@login_required
def export_pdf():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        return "Install reportlab: pip install reportlab", 500

    user  = session["user"]
    rows  = db.view_expenses_records(user)
    total = sum(r[2] for r in rows)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=40, rightMargin=40,
                            topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story  = []

    story.append(Paragraph("Expense Ledger Report", styles["Title"]))
    story.append(Paragraph(
        f"Generated: {date.today().strftime('%d %B %Y')} | User: {user}",
        styles["Normal"]))
    story.append(Spacer(1, 16))

    data = [["ID", "Title", "Amount (₹)", "Category", "Date"]]
    for r in rows:
        data.append([str(r[0]), r[1], f"₹{r[2]:,.2f}", r[3], str(r[4])])
    data.append(["", "TOTAL", f"₹{total:,.2f}", "", ""])

    t = Table(data, colWidths=[35, 200, 90, 90, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  colors.HexColor("#1a2035")),
        ("TEXTCOLOR",    (0,0), (-1,0),  colors.white),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("ALIGN",        (1,1), (1,-1),  "LEFT"),
        ("ROWBACKGROUNDS",(0,1),(-1,-2), [colors.HexColor("#f7f9ff"), colors.white]),
        ("FONTNAME",     (0,-1),(-1,-1), "Helvetica-Bold"),
        ("BACKGROUND",   (0,-1),(-1,-1), colors.HexColor("#e8eaf6")),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#c8d0e8")),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
    ]))
    story.append(t)
    doc.build(story)

    buf.seek(0)
    return send_file(buf, as_attachment=True,
                     download_name=f"expenses_{date.today()}.pdf",
                     mimetype="application/pdf")

if __name__ == "__main__":
    print("\n Expense Ledger Web App")
    print(" Open http://localhost:5000 in your browser")
    print(" Default login: admin / admin123\n")
    app.run(debug=True, port=5000)
