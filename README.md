# 💰 Expense Ledger

A full-featured personal finance tracker built with **Python**, **Flask**, and **SQLite**.
Track expenses, income, and savings — available as both a **Desktop App** and a **Live Web App**.

🌐 **Live Demo:** [https://expense-ledger.onrender.com](https://expense-ledger.onrender.com)  
📦 **GitHub:** [https://github.com/babyaga852/expense-ledger](https://github.com/babyaga852/expense-ledger)

---

## ✨ Features

- 🔐 Login & Registration with password protection
- 📊 Dashboard with stats, charts & recent transactions
- ➕ Add, edit, delete expenses
- 💰 Income tracking with category breakdown
- 📈 Net savings calculation (Income − Expenses)
- 🔍 Search and filter expenses
- 📅 Monthly report with category breakdown & progress bars
- 📑 Export to Excel (.xlsx)
- 📄 Export to PDF
- 🌙 Dark / ☀️ Light mode toggle (remembers your preference)
- 🖥️ Desktop App (Tkinter) + 🌐 Web App (Flask)
- 👤 Per-user data — each user sees only their own records

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | HTML, CSS, Chart.js |
| Desktop | Tkinter |
| Exports | openpyxl, reportlab |
| Deployment | Render (free tier) |

---

## 📁 Folder Structure

```
expense_app/
├── app.py              ← Flask web server
├── tracker.py          ← Shared SQLite database
├── project.py          ← Desktop app (Tkinter)
├── launcher.py         ← App launcher (choose Desktop or Web)
├── requirements.txt    ← Python dependencies
├── Procfile            ← Render deployment config
├── run.bat             ← Quick launch on Windows
└── templates/
    ├── index.html      ← Main web app UI
    └── login.html      ← Login / Register page
```

---

## ⚙️ Setup (One Time Only)

```bash
pip install flask openpyxl reportlab gunicorn
```

---

## 🖥️ Run the Desktop App

```bash
python project.py
```

---

## 🌐 Run the Web App Locally

```bash
python app.py
```

Then open your browser and go to:
```
http://localhost:5000
```

**Default login:**
- Username: `admin`
- Password: `admin123`

> ⚠️ Change your password after first login!

---

## 🚀 Run the Launcher (Choose Mode)

```bash
python launcher.py
```

Choose between:
- 🖥️ **Desktop App** — runs the Tkinter GUI
- 🌐 **Web App (Browser)** — opens the live Render URL
- ⚡ **Both Together** — runs desktop + web simultaneously

---

## 🌍 Live Web App

The web app is deployed globally on Render:

🔗 **[https://expense-ledger.onrender.com](https://expense-ledger.onrender.com)**

> **Note:** Free tier sleeps after inactivity. First load may take 30–60 seconds to wake up.

---

## 📦 Build Windows Installer (.exe)

```bash
python -m PyInstaller --clean ExpenseLedger.spec
```

Then use **Inno Setup** with `setup.iss` to create the installer:
```
installer_output/ExpenseLedger_Setup_v1.1.exe
```

---

## 👤 Author

**Vasudeo Bhoyar**  
GitHub: [@babyaga852](https://github.com/babyaga852)


