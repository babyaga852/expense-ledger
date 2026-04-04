# Expense Ledger — Complete App

Both the **desktop app** and **web app** share the same database (expenses.db).

---

## Folder Structure

```
expense_app/
    ├── tracker.py        ← shared database (SQLite)
    ├── project.py        ← desktop app (tkinter)
    ├── app.py            ← web server (Flask)
    ├── README.txt        ← this file
    └── templates/
        ├── login.html
        └── index.html
```

---

## Setup (one time only)

Open PowerShell in this folder and run:

```
pip install flask openpyxl reportlab
```

---

## Run the Desktop App

```
python project.py
```

---

## Run the Web App

```
python app.py
```

Then open your browser and go to:
```
http://localhost:5000
```

Default login:
- Username: admin
- Password: admin123

Change your password after first login!

---

## Web App Features

- Login / password protection
- Dashboard with stats
- Add, edit, delete expenses
- Search and filter
- Monthly report with category breakdown
- Export to Excel (.xlsx)
- Export to PDF

---

## Selling This App

To run this on a server so anyone can access it from anywhere:

1. Get a cheap VPS (DigitalOcean, Hostinger, etc.) — ~$5/month
2. Install Python + Flask on the server
3. Use gunicorn + nginx to serve it
4. Point a domain name to the server IP

Then sell access as a monthly subscription!
