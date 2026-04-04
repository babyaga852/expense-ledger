from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from datetime import datetime, date
import os, io

import tracker as db

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "expense_ledger_secret_2026"

db.seed_admin()

CATS = ["Food", "Transport", "Shopping", "Bills",
        "Health", "Entertainment", "Education", "Other"]

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
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/change-password", methods=["POST"])
@login_required
def change_password():
    new_pw = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")
    if new_pw != confirm:
        return jsonify({"ok": False, "msg": "Passwords do not match."})
    if len(new_pw) < 6:
        return jsonify({"ok": False, "msg": "Password must be at least 6 characters."})
    db.change_password(session["user"], new_pw)
    return jsonify({"ok": True, "msg": "Password changed successfully."})


# ── Main routes ───────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def dashboard():
    rows  = db.view_expenses_records()
    stats = db.get_all_stats()
    today = date.today()
    monthly = sum(r[2] for r in rows
                  if str(r[3+1]).startswith(f"{today.year}-{today.month:02d}"))
    recent = rows[:8]
    return render_template("index.html",
        page="dashboard", stats=stats, recent=recent,
        monthly=monthly, today=today, cats=CATS,
        user=session["user"])


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    msg = None
    error = None
    if request.method == "POST":
        title    = request.form.get("title", "").strip()
        amount_s = request.form.get("amount", "").strip()
        category = request.form.get("category", "")
        date_s   = request.form.get("date", "")
        try:
            amount = float(amount_s)
            datetime.strptime(date_s, "%Y-%m-%d")
            db.add_expense_record(title, amount, category, date_s)
            msg = f"Added ₹{amount:,.2f} — {title}"
        except ValueError as e:
            error = str(e)
    return render_template("index.html", page="add", cats=CATS,
                           msg=msg, error=error,
                           today=date.today(), user=session["user"])


@app.route("/expenses")
@login_required
def expenses():
    q    = request.args.get("q", "").lower()
    rows = db.view_expenses_records()
    if q:
        rows = [r for r in rows
                if q in r[1].lower() or q in r[3].lower() or q in str(r[4])]
    return render_template("index.html", page="expenses",
                           rows=rows, q=q, cats=CATS,
                           today=date.today(), user=session["user"])


@app.route("/delete/<int:eid>", methods=["POST"])
@login_required
def delete(eid):
    db.delete_expense_by_id(eid)
    return redirect(url_for("expenses"))


@app.route("/update/<int:eid>", methods=["POST"])
@login_required
def update(eid):
    amt_s = request.form.get("amount", "").strip()
    title = request.form.get("title", "").strip()
    cat   = request.form.get("category", "").strip()
    if amt_s:
        try:    db.update_expense_amount(eid, float(amt_s))
        except: pass
    if title:
        db.update_expense_title(eid, title)
    if cat and cat != "(keep)":
        db.update_expense_category(eid, cat)
    return redirect(url_for("expenses"))


@app.route("/report")
@login_required
def report():
    today = date.today()
    m  = int(request.args.get("month", today.month))
    yr = int(request.args.get("year",  today.year))
    rows  = db.get_expenses_for_month(m, yr)
    total = sum(r[2] for r in rows)
    cat_t = {}
    for r in rows:
        cat_t[r[3]] = cat_t.get(r[3], 0) + r[2]
    cat_data = sorted(cat_t.items(), key=lambda x: -x[1])
    month_name = datetime(2000, m, 1).strftime("%B")
    return render_template("index.html", page="report",
                           rows=rows, total=total, cat_data=cat_data,
                           month=m, year=yr, month_name=month_name,
                           cats=CATS, today=today, user=session["user"])


# ── Export routes ─────────────────────────────────────────────────────────────
@app.route("/export/excel")
@login_required
def export_excel():
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
    except ImportError:
        return "Install openpyxl first:  pip install openpyxl", 500

    rows = db.view_expenses_records()
    wb = openpyxl.Workbook()
    ws = wb.active
    if ws is None:
        ws = wb.create_sheet("Expenses")
    else:
        ws.title = "Expenses"

    # Header style
    hdr_font = Font(bold=True, color="FFFFFF", size=11)
    hdr_fill = PatternFill("solid", fgColor="1a2035")
    headers  = ["ID", "Title", "Amount (Rs.)", "Category", "Date"]
    col_w    = [8, 35, 18, 18, 15]

    for i, (h, w) in enumerate(zip(headers, col_w), 1):
        c = ws.cell(row=1, column=i, value=h)
        c.font      = hdr_font
        c.fill      = hdr_fill
        c.alignment = Alignment(horizontal="center")
        ws.column_dimensions[c.column_letter].width = w

    # Data rows
    for ri, row in enumerate(rows, 2):
        for ci, val in enumerate(row, 1):
            c = ws.cell(row=ri, column=ci, value=val)
            c.alignment = Alignment(horizontal="center" if ci != 2 else "left")
        ws.cell(row=ri, column=3).number_format = "#,##0.00"

    # Total row
    last = len(rows) + 2
    ws.cell(row=last, column=2, value="TOTAL").font = Font(bold=True)
    ws.cell(row=last, column=3,
            value=sum(r[2] for r in rows)).font = Font(bold=True)
    ws.cell(row=last, column=3).number_format = "#,##0.00"

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
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
        return "Install reportlab first:  pip install reportlab", 500

    rows  = db.view_expenses_records()
    total = sum(r[2] for r in rows)
    buf   = io.BytesIO()
    doc   = SimpleDocTemplate(buf, pagesize=A4,
                              leftMargin=40, rightMargin=40,
                              topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story  = []

    # Title
    title_style = styles["Title"]
    story.append(Paragraph("Expense Ledger Report", title_style))
    story.append(Paragraph(
        f"Generated: {date.today().strftime('%d %B %Y')}  |  User: {session['user']}",
        styles["Normal"]))
    story.append(Spacer(1, 16))

    # Table data
    data = [["ID", "Title", "Amount (Rs.)", "Category", "Date"]]
    for r in rows:
        data.append([str(r[0]), r[1], f"Rs.{r[2]:,.2f}", r[3], str(r[4])])
    data.append(["", "TOTAL", f"Rs.{total:,.2f}", "", ""])

    t = Table(data, colWidths=[35, 200, 90, 90, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a2035")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 10),
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",      (1, 1), (1, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2),
         [colors.HexColor("#f7f9ff"), colors.white]),
        ("FONTNAME",   (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8eaf6")),
        ("GRID",       (0, 0), (-1, -1), 0.4, colors.HexColor("#c8d0e8")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    doc.build(story)
    buf.seek(0)
    return send_file(buf, as_attachment=True,
                     download_name=f"expenses_{date.today()}.pdf",
                     mimetype="application/pdf")


if __name__ == "__main__":
    print("\n  Expense Ledger Web App")
    print("  Open http://localhost:5000 in your browser")
    print("  Default login:  admin / admin123\n")
    app.run(debug=True, port=5000)
