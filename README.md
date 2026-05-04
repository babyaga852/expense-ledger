![Expense Ledger Logo](expense_ledger_logo.png)

# 💰 Expense Ledger

A full-featured personal finance tracker built with **Python**. Track expenses, income, and savings — available as both a **Desktop App** and **Web App**.

🌐 **Live Demo:** [https://babayaga3.pythonanywhere.com](https://babayaga3.pythonanywhere.com)  
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
- 🌙 Dark / ☀️ Light mode toggle
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
| Packaging | PyInstaller |

---

## 📁 Folder Structure

```
expense-ledger/
├── app.py              ← Flask web server
├── tracker.py          ← Database operations
├── project.py          ← Desktop app (Tkinter)
├── launcher.py         ← App launcher
├── ExpenseLedger.spec  ← PyInstaller config
├── install_linux.sh    ← Linux installer
├── install_mac.sh      ← Mac installer
├── install.bat         ← Windows installer
├── requirements.txt   ← Python dependencies
├── templates/
│   └── index.html     ← Web app UI
└── dist/
    └── ExpenseLedger/  ← Built app
```

---

## 💾 Where Data is Stored

Desktop app: `~/.expense_ledger/desktop.db`  
Web app: `~/.expense_ledger/expenses.db`

---

## 🚀 Quick Install

### Linux
```bash
bash install_linux.sh
```

### Mac
```bash
chmod +x install_mac.sh
./install_mac.sh
```

### Windows
Double-click `install.bat`

---

## 🖥️ Run the Desktop App (Built)

```bash
# After install:
~/Applications/ExpenseLedger/ExpenseLedger
```

Or run directly from project:
```bash
python project.py
```

---

## 🌐 Run the Web App Locally

```bash
python app.py
```

Open: `http://localhost:5000`

**Default login:**
- Username: `admin`
- Password: `admin123`

---

## 🌐 Live Web App

🔗 **[https://babayaga3.pythonanywhere.com](https://babayaga3.pythonanywhere.com)**

> Free tier may take 30-60 seconds to wake up.

---

## 🔨 Build from Source

```bash
# Create venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install flask werkzeug openpyxl reportlab pyinstaller pillow

# Build
pyinstaller ExpenseLedger.spec

# Install
bash install_linux.sh  # Linux
# or: ./install_mac.sh  # Mac
# or: install.bat  # Windows
```

---

## 👤 Author

**Your Name**  
GitHub: [@babyaga852](https://github.com/babyaga852)