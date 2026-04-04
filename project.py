import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import os
import types

try:
    import tracker as tracker
except ImportError:
    class TrackerStub:
        @staticmethod
        def add_expense_record(t, a, c, d): pass
        @staticmethod
        def view_expenses_records(): return []
        @staticmethod
        def delete_expense_by_id(e): return True
        @staticmethod
        def update_expense_amount(e, a): return True
        @staticmethod
        def update_expense_title(e, t): return True
        @staticmethod
        def update_expense_category(e, c): return True
        @staticmethod
        def monthly_report_total(m): return 0.0
    
    tracker = TrackerStub()

_HERE = os.path.dirname(os.path.abspath(__file__))

# ── Theme Palettes ────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "BG":       "#0d1117",
        "BG2":      "#161b27",
        "CARD":     "#1a2035",
        "CARD2":    "#1f2640",
        "BORDER":   "#2a3350",
        "BORDER2":  "#334070",
        "FG":       "#e8eaf6",
        "FG2":      "#8892b0",
        "FG3":      "#4a5568",
    },
    "light": {
        "BG":       "#f0f4ff",
        "BG2":      "#e2e8f8",
        "CARD":     "#ffffff",
        "CARD2":    "#f7f9ff",
        "BORDER":   "#c8d0e8",
        "BORDER2":  "#b0bcd8",
        "FG":       "#1a1f2e",
        "FG2":      "#4a5568",
        "FG3":      "#94a3b8",
    },
}

# Shared accent colours (same in both modes)
GOLD     = "#c9a84c"
GOLD2    = "#e8c76a"
GOLD_DIM = "#7a5f28"
TEAL     = "#2dd4bf"
RED      = "#f87171"
GREEN    = "#4ade80"
AMBER    = "#fbbf24"
BLUE     = "#60a5fa"
PINK     = "#f472b6"
WHITE    = "#ffffff"

CATS = ["Food", "Transport", "Shopping", "Bills",
        "Health", "Entertainment", "Education", "Other"]

CAT_META = {
    "Food":          ("#fbbf24", "~"),
    "Transport":     ("#60a5fa", ">"),
    "Shopping":      ("#f472b6", "*"),
    "Bills":         ("#f87171", "!"),
    "Health":        ("#4ade80", "+"),
    "Entertainment": ("#a78bfa", "@"),
    "Education":     ("#2dd4bf", "#"),
    "Other":         ("#8892b0", "."),
}

def cat_color(c): return CAT_META.get(c, ("#8892b0", "."))[0]
def cat_icon(c):  return CAT_META.get(c, ("#8892b0", "."))[1]

# ── Theme state (mutable globals) ─────────────────────────────────────────────
_mode = "dark"

def T(key):
    return THEMES[_mode][key]

# shortcuts
def BG():    return T("BG")
def BG2():   return T("BG2")
def CARD():  return T("CARD")
def CARD2(): return T("CARD2")
def BORDER():  return T("BORDER")
def BORDER2(): return T("BORDER2")
def FG():    return T("FG")
def FG2():   return T("FG2")
def FG3():   return T("FG3")

# ── Splash ────────────────────────────────────────────────────────────────────
def _splash(root):
    s = tk.Toplevel(root)
    s.overrideredirect(True)
    s.configure(bg=BG())
    w, h = 380, 220
    sw, sh = s.winfo_screenwidth(), s.winfo_screenheight()
    s.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    tk.Frame(s, bg=GOLD, height=2).pack(fill="x")
    body = tk.Frame(s, bg=BG())
    body.pack(fill="both", expand=True, padx=32, pady=24)
    tk.Label(body, text="Rs.", font=("Georgia", 32, "bold"),
             bg=BG(), fg=GOLD).pack()
    tk.Label(body, text="EXPENSE LEDGER",
             font=("Georgia", 14, "bold"), bg=BG(), fg=FG()).pack(pady=(4, 2))
    tk.Label(body, text="Personal Finance Manager",
             font=("Segoe UI", 9), bg=BG(), fg=FG3()).pack()
    bar_bg = tk.Frame(body, bg=BORDER(), height=2)
    bar_bg.pack(fill="x", pady=(20, 0))
    bar = tk.Frame(bar_bg, bg=GOLD, height=2, width=0)
    bar.place(x=0, y=0, relheight=1)
    def _anim(v=0):
        if v <= 316:
            bar.place(x=0, y=0, width=v, relheight=1)
            s.after(5, _anim, v + 6)
    _anim()
    s.update()
    return s

# ── Widgets ───────────────────────────────────────────────────────────────────
class StyledEntry(tk.Frame):
    def __init__(self, parent, label, **kw):
        super().__init__(parent, bg=CARD2(), highlightthickness=1,
                         highlightbackground=BORDER())
        tk.Label(self, text=label, font=("Segoe UI", 7, "bold"),
                 bg=CARD2(), fg=GOLD).pack(anchor="w", padx=12, pady=(8, 0))
        self.var = tk.StringVar()
        self._e = tk.Entry(self, textvariable=self.var, bg=CARD2(), fg=FG(),
                           insertbackground=GOLD, relief="flat",
                           font=("Segoe UI", 11), bd=0, **kw)
        self._e.pack(fill="x", padx=12, pady=(2, 10))
        self._e.bind("<FocusIn>",
                     lambda e: self.configure(highlightbackground=GOLD))
        self._e.bind("<FocusOut>",
                     lambda e: self.configure(highlightbackground=BORDER()))

    def get(self): return self.var.get().strip()
    def set(self, v): self.var.set(v)
    def clear(self): self.var.set("")


class StyledDropdown(tk.Frame):
    def __init__(self, parent, label, values):
        super().__init__(parent, bg=CARD2(), highlightthickness=1,
                         highlightbackground=BORDER())
        tk.Label(self, text=label, font=("Segoe UI", 7, "bold"),
                 bg=CARD2(), fg=GOLD).pack(anchor="w", padx=12, pady=(8, 0))
        self.var = tk.StringVar(value=values[0])
        st = ttk.Style()
        st.configure("Gold.TCombobox", fieldbackground=CARD2(),
                     background=CARD2(), foreground=FG(), arrowcolor=GOLD,
                     selectbackground=GOLD_DIM, selectforeground=WHITE)
        self._cb = ttk.Combobox(self, textvariable=self.var, values=values,
                          state="readonly", style="Gold.TCombobox",
                          font=("Segoe UI", 11))
        self._cb.pack(fill="x", padx=8, pady=(2, 10))
        self._cb.bind("<FocusIn>",
                lambda e: self.configure(highlightbackground=GOLD))
        self._cb.bind("<FocusOut>",
                lambda e: self.configure(highlightbackground=BORDER()))

    def get(self): return self.var.get()
    def set(self, v): self.var.set(v)


def gold_btn(parent, text, cmd, bg=None, fg=None):
    bg = bg or GOLD
    fg = fg or BG()
    f = tk.Frame(parent, bg=bg, cursor="hand2")
    lb = tk.Label(f, text=text, bg=bg, fg=fg,
                  font=("Segoe UI", 10, "bold"), padx=20, pady=9)
    lb.pack()
    for x in (f, lb):
        x.bind("<Button-1>", lambda e: cmd())
        x.bind("<Enter>",
               lambda e: [f.configure(bg=GOLD2), lb.configure(bg=GOLD2)])
        x.bind("<Leave>",
               lambda e: [f.configure(bg=bg), lb.configure(bg=bg)])
    return f


def ghost_btn(parent, text, cmd):
    f = tk.Frame(parent, bg=CARD(), cursor="hand2",
                 highlightthickness=1, highlightbackground=BORDER2())
    lb = tk.Label(f, text=text, bg=CARD(), fg=FG2(),
                  font=("Segoe UI", 9), padx=14, pady=6)
    lb.pack()
    for x in (f, lb):
        x.bind("<Button-1>", lambda e: cmd())
        x.bind("<Enter>",
               lambda e: [f.configure(highlightbackground=GOLD),
                          lb.configure(fg=GOLD)])
        x.bind("<Leave>",
               lambda e: [f.configure(highlightbackground=BORDER2()),
                          lb.configure(fg=FG2())])
    return f


def stat_card(parent, label, value, sub, color, symbol):
    f = tk.Frame(parent, bg=CARD(), highlightthickness=1,
                 highlightbackground=BORDER())
    top = tk.Frame(f, bg=CARD())
    top.pack(fill="x", padx=16, pady=(14, 0))
    tk.Label(top, text=symbol, font=("Segoe UI", 12),
             bg=CARD(), fg=color).pack(side="left")
    tk.Label(top, text=label, font=("Segoe UI", 9),
             bg=CARD(), fg=FG3()).pack(side="left", padx=6)
    tk.Label(f, text=value, font=("Georgia", 20, "bold"),
             bg=CARD(), fg=color).pack(anchor="w", padx=16, pady=(4, 0))
    tk.Label(f, text=sub, font=("Segoe UI", 8),
             bg=CARD(), fg=FG3()).pack(anchor="w", padx=16, pady=(0, 14))
    return f


def show_toast(root, msg, color=GREEN):
    t = tk.Toplevel(root)
    t.overrideredirect(True)
    t.attributes("-topmost", True)
    t.configure(bg=color)
    tk.Frame(t, bg=color, height=3).pack(fill="x")
    tk.Label(t, text=msg, bg=color, fg=BG(),
             font=("Segoe UI", 10, "bold"), padx=24, pady=10).pack()
    x = root.winfo_x() + root.winfo_width() // 2 - 160
    y = root.winfo_y() + root.winfo_height() - 72
    t.geometry(f"+{x}+{y}")
    t.after(2400, t.destroy)

# ── Main App ──────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        sp = _splash(self)
        self.after(2000, lambda: self._init(sp))

    def _init(self, sp):
        sp.destroy()
        self.title("Expense Ledger")
        self.configure(bg=BG())
        self.geometry("960x640")
        self.minsize(800, 520)
        try:
            self.iconbitmap(os.path.join(_HERE, "expense_tracker.ico"))
        except:
            pass
        self._page = "dashboard"
        self._build()
        self.deiconify()

    def _build(self):
        self._sb = tk.Frame(self, bg=BG2(), width=220)
        self._sb.pack(side="left", fill="y")
        self._sb.pack_propagate(False)
        self._div = tk.Frame(self, bg=BORDER(), width=1)
        self._div.pack(side="left", fill="y")
        self._main = tk.Frame(self, bg=BG())
        self._main.pack(side="left", fill="both", expand=True)
        self._build_sidebar()
        self._go("dashboard")

    def _build_sidebar(self):
        sb = self._sb
        # Logo
        logo = tk.Frame(sb, bg=BG2(), height=72)
        logo.pack(fill="x")
        logo.pack_propagate(False)
        self._logo_bar = tk.Frame(logo, bg=GOLD, width=3)
        self._logo_bar.pack(side="left", fill="y")
        inner = tk.Frame(logo, bg=BG2())
        inner.pack(side="left", fill="both", expand=True, padx=16)
        tk.Label(inner, text="Rs.", font=("Georgia", 18, "bold"),
                 bg=BG2(), fg=GOLD).pack(side="left")
        nf = tk.Frame(inner, bg=BG2())
        nf.pack(side="left", padx=8)
        tk.Label(nf, text="EXPENSE", font=("Georgia", 10, "bold"),
                 bg=BG2(), fg=FG()).pack(anchor="w")
        tk.Label(nf, text="LEDGER", font=("Georgia", 8),
                 bg=BG2(), fg=GOLD).pack(anchor="w")

        # Theme toggle button in sidebar header
        self._theme_btn = tk.Label(inner, text="☀" if _mode == "dark" else "🌙",
                                   font=("Segoe UI Emoji", 14),
                                   bg=BG2(), fg=GOLD, cursor="hand2")
        self._theme_btn.pack(side="right", padx=4)
        self._theme_btn.bind("<Button-1>", lambda e: self._toggle_theme())

        tk.Frame(sb, bg=BORDER(), height=1).pack(fill="x")
        tk.Frame(sb, bg=BG2(), height=8).pack(fill="x")

        nav = [
            ("dashboard", "[H]", "Dashboard"),
            ("add",       "[+]", "Add Expense"),
            ("view",      "[=]", "All Expenses"),
            ("modify",    "[E]", "Edit / Delete"),
            ("report",    "[R]", "Monthly Report"),
        ]
        self._nav = {}
        for key, ico, lbl in nav:
            self._nav[key] = self._nav_item(sb, key, ico, lbl)

        tk.Frame(sb, bg=BG2()).pack(fill="both", expand=True)
        tk.Frame(sb, bg=BORDER(), height=1).pack(fill="x")
        self._bot = tk.Frame(sb, bg=BG2())
        self._bot.pack(fill="x", padx=16, pady=12)
        tk.Label(self._bot, text=date.today().strftime("%d %B %Y"),
                 font=("Segoe UI", 9), bg=BG2(), fg=FG3()).pack(anchor="w")
        tk.Label(self._bot, text="Personal Finance v2.0",
                 font=("Segoe UI", 8), bg=BG2(), fg=FG3()).pack(anchor="w")

    def _nav_item(self, parent, key, ico, lbl):
        f = tk.Frame(parent, bg=BG2(), cursor="hand2", height=46)
        f.pack(fill="x")
        f.pack_propagate(False)
        bar = tk.Frame(f, bg=BG2(), width=3)
        bar.pack(side="left", fill="y")
        row = tk.Frame(f, bg=BG2())
        row.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ico_l = tk.Label(row, text=ico, font=("Courier", 10, "bold"),
                         bg=BG2(), fg=FG3(), width=4)
        ico_l.pack(side="left")
        txt_l = tk.Label(row, text=lbl, font=("Segoe UI", 10),
                         bg=BG2(), fg=FG3())
        txt_l.pack(side="left", padx=4)

        def click(): self._go(key)
        def enter(e):
            if self._page != key:
                for w in [f, row, ico_l, txt_l]: w.configure(bg=CARD())
        def leave(e):
            if self._page != key:
                for w in [f, row, ico_l, txt_l]: w.configure(bg=BG2())

        for w in [f, row, ico_l, txt_l]:
            w.bind("<Button-1>", lambda e: click())
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)

        return {"f": f, "bar": bar, "row": row, "ico": ico_l, "txt": txt_l}

    # ── Theme toggle ──────────────────────────────────────────────────────
    def _toggle_theme(self):
        global _mode
        _mode = "light" if _mode == "dark" else "dark"
        # Full rebuild
        for w in self.winfo_children():
            w.destroy()
        self.configure(bg=BG())
        self._page = self._page if hasattr(self, "_page") else "dashboard"
        self._build()
        # Update toggle icon
        self._theme_btn.configure(
            text="☀" if _mode == "dark" else "🌙")

    def _go(self, key):
        if hasattr(self, "_nav") and self._page in self._nav:
            n = self._nav[self._page]
            for w in [n["f"], n["row"], n["ico"], n["txt"]]:
                w.configure(bg=BG2())
            n["bar"].configure(bg=BG2())
            n["ico"].configure(fg=FG3())
            n["txt"].configure(fg=FG3(), font=("Segoe UI", 10))
        self._page = key
        n = self._nav[key]
        for w in [n["f"], n["row"], n["ico"], n["txt"]]:
            w.configure(bg=CARD())
        n["bar"].configure(bg=GOLD)
        n["ico"].configure(fg=GOLD)
        n["txt"].configure(fg=FG(), font=("Segoe UI", 10, "bold"))
        for w in self._main.winfo_children():
            w.destroy()
        {"dashboard": self._pg_dash, "add": self._pg_add,
         "view": self._pg_view, "modify": self._pg_modify,
         "report": self._pg_report}[key]()

    def _hdr(self, title, sub=""):
        h = tk.Frame(self._main, bg=BG())
        h.pack(fill="x", padx=28, pady=(22, 0))
        # Theme toggle button top-right
        tog = tk.Label(h,
                       text=("☀  Light Mode" if _mode == "dark" else "🌙  Dark Mode"),
                       font=("Segoe UI", 9), bg=BG(), fg=GOLD, cursor="hand2")
        tog.pack(side="right")
        tog.bind("<Button-1>", lambda e: self._toggle_theme())

        tk.Label(h, text=title, font=("Georgia", 20, "bold"),
                 bg=BG(), fg=FG()).pack(anchor="w")
        if sub:
            tk.Label(h, text=sub, font=("Segoe UI", 9),
                     bg=BG(), fg=FG3()).pack(anchor="w", pady=(2, 0))
        ul = tk.Frame(self._main, bg=BORDER(), height=1)
        ul.pack(fill="x", padx=28, pady=(10, 0))
        tk.Frame(ul, bg=GOLD, height=1, width=60).place(x=0, y=0)

    # ── Dashboard ─────────────────────────────────────────────────────────
    def _pg_dash(self):
        self._hdr("Dashboard",
                  date.today().strftime("%A, %d %B %Y") +
                  "  —  Your financial overview")
        try:    rows = tracker.view_expenses_records()
        except: rows = []

        total   = sum(r[2] for r in rows)
        month   = date.today().month
        year    = date.today().year
        monthly = sum(r[2] for r in rows
                      if str(r[4]).startswith(f"{year}-{month:02d}"))
        count   = len(rows)
        avg     = total / count if count else 0

        sc = tk.Frame(self._main, bg=BG())
        sc.pack(fill="x", padx=28, pady=18)
        for i in range(4): sc.columnconfigure(i, weight=1, uniform="s")

        stat_card(sc, "Total Spent",   f"Rs.{total:,.0f}",
                  f"{count} transactions", GOLD,  "[Rs]").grid(
            row=0, column=0, sticky="ew", padx=(0, 6))
        stat_card(sc, "This Month",    f"Rs.{monthly:,.0f}",
                  date.today().strftime("%B %Y"), TEAL, "[M]").grid(
            row=0, column=1, sticky="ew", padx=3)
        stat_card(sc, "Transactions",  str(count),
                  "all time", BLUE, "[N]").grid(
            row=0, column=2, sticky="ew", padx=3)
        stat_card(sc, "Avg per Entry", f"Rs.{avg:,.0f}",
                  "per transaction", PINK, "[~]").grid(
            row=0, column=3, sticky="ew", padx=(6, 0))

        lower = tk.Frame(self._main, bg=BG())
        lower.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        lower.columnconfigure(0, weight=3)
        lower.columnconfigure(1, weight=2)

        rc = tk.Frame(lower, bg=CARD(), highlightthickness=1,
                      highlightbackground=BORDER())
        rc.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        rh = tk.Frame(rc, bg=CARD())
        rh.pack(fill="x", padx=16, pady=(14, 0))
        tk.Label(rh, text="Recent Transactions",
                 font=("Georgia", 12, "bold"), bg=CARD(), fg=FG()).pack(side="left")
        ghost_btn(rh, "View all ->", lambda: self._go("view")).pack(side="right")
        tk.Frame(rc, bg=BORDER(), height=1).pack(fill="x", padx=16, pady=8)
        sf = tk.Frame(rc, bg=CARD())
        sf.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        if not rows:
            tk.Label(sf, text="No transactions yet.",
                     font=("Segoe UI", 10), bg=CARD(), fg=FG3()).pack(pady=24)
        else:
            for r in list(reversed(rows))[:8]:
                self._tx_row(sf, *r)

        cc = tk.Frame(lower, bg=CARD(), highlightthickness=1,
                      highlightbackground=BORDER())
        cc.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(cc, text="By Category",
                 font=("Georgia", 12, "bold"), bg=CARD(), fg=FG()).pack(
            anchor="w", padx=16, pady=(14, 8))
        tk.Frame(cc, bg=BORDER(), height=1).pack(fill="x", padx=16, pady=(0, 8))
        cat_t = {}
        for r in rows: cat_t[r[3]] = cat_t.get(r[3], 0) + r[2]
        if not cat_t:
            tk.Label(cc, text="No data yet.",
                     font=("Segoe UI", 10), bg=CARD(), fg=FG3()).pack(pady=20)
        else:
            for cat, amt in sorted(cat_t.items(), key=lambda x: -x[1])[:6]:
                pct = amt / total if total else 0
                self._cat_row(cc, cat, amt, pct)

    def _tx_row(self, parent, eid, title, amount, category, date_val):
        row = tk.Frame(parent, bg=CARD2(), highlightthickness=1,
                       highlightbackground=BORDER())
        row.pack(fill="x", pady=2, padx=2)
        cc = cat_color(category)
        tk.Frame(row, bg=cc, width=3).pack(side="left", fill="y")
        left = tk.Frame(row, bg=CARD2())
        left.pack(side="left", fill="both", expand=True, padx=10, pady=7)
        tk.Label(left, text=title, font=("Segoe UI", 10, "bold"),
                 bg=CARD2(), fg=FG()).pack(anchor="w")
        tk.Label(left, text=f"{cat_icon(category)} {category}   {date_val}",
                 font=("Segoe UI", 8), bg=CARD2(), fg=FG3()).pack(anchor="w")
        tk.Label(row, text=f"Rs.{amount:,.2f}",
                 font=("Segoe UI", 11, "bold"),
                 bg=CARD2(), fg=cc, anchor="e", width=12).pack(
            side="right", padx=12)

    def _cat_row(self, parent, cat, amt, pct):
        f = tk.Frame(parent, bg=CARD())
        f.pack(fill="x", padx=16, pady=3)
        cc = cat_color(cat)
        top = tk.Frame(f, bg=CARD())
        top.pack(fill="x")
        tk.Label(top, text=f"{cat_icon(cat)} {cat}",
                 font=("Segoe UI", 9), bg=CARD(), fg=FG2()).pack(side="left")
        tk.Label(top, text=f"Rs.{amt:,.0f}  ({pct*100:.0f}%)",
                 font=("Segoe UI", 9, "bold"), bg=CARD(), fg=FG()).pack(side="right")
        bar_bg = tk.Frame(f, bg=BORDER(), height=5)
        bar_bg.pack(fill="x", pady=(3, 0))
        def _draw(e=None, p=pct, c=cc, b=bar_bg):
            b.update_idletasks()
            w = int(b.winfo_width() * p)
            tk.Frame(b, bg=c, height=5, width=max(4, w)).place(x=0, y=0)
        bar_bg.bind("<Configure>", _draw)

    # ── Add Expense ───────────────────────────────────────────────────────
    def _pg_add(self):
        self._hdr("Add Expense", "Record a new transaction to your ledger")
        outer = tk.Frame(self._main, bg=BG())
        outer.pack(fill="both", expand=True, padx=28, pady=18)

        fc = tk.Frame(outer, bg=CARD(), highlightthickness=1,
                      highlightbackground=BORDER())
        fc.pack(fill="x")
        tk.Frame(fc, bg=GOLD, height=2).pack(fill="x")
        form = tk.Frame(fc, bg=CARD())
        form.pack(fill="x", padx=24, pady=20)
        form.columnconfigure((0, 1), weight=1)

        self._a_title  = StyledEntry(form, "TITLE")
        self._a_title.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=6)
        self._a_amount = StyledEntry(form, "AMOUNT (Rs.)")
        self._a_amount.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=6)
        self._a_cat    = StyledDropdown(form, "CATEGORY", CATS)
        self._a_cat.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=6)
        self._a_date   = StyledEntry(form, "DATE (YYYY-MM-DD)")
        self._a_date.set(date.today().isoformat())
        self._a_date.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=6)

        br = tk.Frame(fc, bg=CARD())
        br.pack(fill="x", padx=24, pady=(0, 20))
        gold_btn(br, "  Add to Ledger  ->", self._do_add).pack(side="left")
        tk.Label(br, text="All fields required",
                 font=("Segoe UI", 8), bg=CARD(), fg=FG3()).pack(
            side="left", padx=14)

        tips = tk.Frame(outer, bg=CARD2(), highlightthickness=1,
                        highlightbackground=BORDER())
        tips.pack(fill="x", pady=(14, 0))
        tk.Label(tips, text="Quick Tips",
                 font=("Segoe UI", 9, "bold"), bg=CARD2(), fg=GOLD).pack(
            anchor="w", padx=16, pady=(12, 4))
        for tip in ["Date format: YYYY-MM-DD  (e.g. 2026-04-03)",
                    "Amount accepts decimals  (e.g. 129.50)",
                    "Consistent categories make better reports"]:
            tk.Label(tips, text=f"  *  {tip}",
                     font=("Segoe UI", 9), bg=CARD2(), fg=FG3()).pack(
                anchor="w", padx=16)
        tk.Frame(tips, bg=CARD2(), height=12).pack()

    def _do_add(self):
        title  = self._a_title.get()
        amt_s  = self._a_amount.get()
        cat    = self._a_cat.get()
        date_s = self._a_date.get()
        if not all([title, amt_s, date_s]):
            messagebox.showerror("Missing Fields", "Please fill all fields.")
            return
        try:    amt = float(amt_s)
        except: messagebox.showerror("Invalid Amount", "Amount must be a number."); return
        try:    datetime.strptime(date_s, "%Y-%m-%d")
        except: messagebox.showerror("Invalid Date", "Use YYYY-MM-DD format."); return
        try:
            tracker.add_expense_record(title, amt, cat, date_s)
            show_toast(self, f"Added  Rs.{amt:,.2f}  -  {title}")
            self._a_title.clear()
            self._a_amount.clear()
            self._a_date.set(date.today().isoformat())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── View All ──────────────────────────────────────────────────────────
    def _pg_view(self):
        self._hdr("All Expenses", "Complete transaction history")
        tb = tk.Frame(self._main, bg=BG())
        tb.pack(fill="x", padx=28, pady=(12, 8))
        ghost_btn(tb, "Refresh", self._refresh_tree).pack(side="left")

        sf = tk.Frame(tb, bg=CARD2(), highlightthickness=1,
                      highlightbackground=BORDER())
        sf.pack(side="right")
        tk.Label(sf, text="Search:", font=("Segoe UI", 9),
                 bg=CARD2(), fg=FG3()).pack(side="left", padx=(10, 2))
        self._sq = tk.StringVar()
        self._sq.trace_add("write", lambda *a: self._filter())
        tk.Entry(sf, textvariable=self._sq, bg=CARD2(), fg=FG(),
                 insertbackground=GOLD, relief="flat",
                 font=("Segoe UI", 10), bd=0, width=22).pack(
            side="left", pady=7, padx=(0, 10))

        tf = tk.Frame(self._main, bg=BG())
        tf.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        st = ttk.Style()
        st.configure("Ledger.Treeview",
            background=CARD(), foreground=FG(),
            fieldbackground=CARD(), rowheight=34,
            borderwidth=0, font=("Segoe UI", 10))
        st.configure("Ledger.Treeview.Heading",
            background=CARD2(), foreground=GOLD,
            font=("Segoe UI", 9, "bold"), borderwidth=0, relief="flat")
        st.map("Ledger.Treeview",
            background=[("selected", GOLD_DIM)],
            foreground=[("selected", WHITE)])

        cols = ("id", "title", "amount", "category", "date")
        self._tv = ttk.Treeview(tf, columns=cols, show="headings",
                                style="Ledger.Treeview")
        for col, w, anc in [("id", 50, "center"), ("title", 240, "w"),
                             ("amount", 120, "e"), ("category", 130, "center"),
                             ("date", 110, "center")]:
            self._tv.heading(col, text=col.upper(),
                command=lambda c=col: self._sort(c, False))
            self._tv.column(col, width=w, anchor=anc)  # type: ignore

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._tv.yview)
        self._tv.configure(yscrollcommand=vsb.set)
        self._tv.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self._rows_cache = []
        self._refresh_tree()

    def _refresh_tree(self):
        for i in self._tv.get_children(): self._tv.delete(i)
        try:    self._rows_cache = list(tracker.view_expenses_records())
        except Exception as e: messagebox.showerror("Error", str(e)); return
        self._filter()

    def _filter(self):
        q = self._sq.get().lower()
        for i in self._tv.get_children(): self._tv.delete(i)
        for r in self._rows_cache:
            eid, title, amt, cat, d = r
            if q in title.lower() or q in cat.lower() or q in str(d):
                self._tv.insert("", tk.END,
                    values=(eid, title, f"Rs.{amt:,.2f}", cat, d))

    def _sort(self, col, rev):
        data = [(self._tv.set(k, col), k) for k in self._tv.get_children("")]
        try:    data.sort(key=lambda t: float(t[0].replace("Rs.","").replace(",","")), reverse=rev)
        except: data.sort(key=lambda t: t[0].lower(), reverse=rev)
        for i, (_, k) in enumerate(data): self._tv.move(k, "", i)
        self._tv.heading(col, command=lambda: self._sort(col, not rev))

    # ── Edit / Delete ─────────────────────────────────────────────────────
    def _pg_modify(self):
        self._hdr("Edit / Delete", "Modify or remove existing transactions")
        outer = tk.Frame(self._main, bg=BG())
        outer.pack(fill="both", expand=True, padx=28, pady=18)
        outer.columnconfigure((0, 1), weight=1)

        dc = tk.Frame(outer, bg=CARD(), highlightthickness=1,
                      highlightbackground=BORDER())
        dc.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Frame(dc, bg=RED, height=2).pack(fill="x")
        tk.Label(dc, text="Delete Transaction",
                 font=("Georgia", 12, "bold"), bg=CARD(), fg=RED).pack(
            anchor="w", padx=16, pady=(14, 4))
        tk.Frame(dc, bg=BORDER(), height=1).pack(fill="x", padx=16)
        df = tk.Frame(dc, bg=CARD())
        df.pack(fill="x", padx=16, pady=16)
        self._d_id = StyledEntry(df, "TRANSACTION ID")
        self._d_id.pack(fill="x", pady=(0, 10))
        gold_btn(df, "Delete Entry", self._do_del, bg=RED, fg=WHITE).pack(anchor="w")
        tk.Label(dc, text="This action cannot be undone",
                 font=("Segoe UI", 8), bg=CARD(), fg=FG3()).pack(
            anchor="w", padx=16, pady=(0, 16))

        uc = tk.Frame(outer, bg=CARD(), highlightthickness=1,
                      highlightbackground=BORDER())
        uc.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Frame(uc, bg=AMBER, height=2).pack(fill="x")
        tk.Label(uc, text="Update Transaction",
                 font=("Georgia", 12, "bold"), bg=CARD(), fg=AMBER).pack(
            anchor="w", padx=16, pady=(14, 4))
        tk.Frame(uc, bg=BORDER(), height=1).pack(fill="x", padx=16)
        uf = tk.Frame(uc, bg=CARD())
        uf.pack(fill="x", padx=16, pady=16)
        uf.columnconfigure((0, 1), weight=1)
        self._u_id  = StyledEntry(uf, "TRANSACTION ID")
        self._u_id.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)
        self._u_amt = StyledEntry(uf, "NEW AMOUNT (blank = keep)")
        self._u_amt.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)
        self._u_ttl = StyledEntry(uf, "NEW TITLE (blank = keep)")
        self._u_ttl.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=4)
        self._u_cat = StyledDropdown(uf, "NEW CATEGORY", ["(keep)"] + CATS)
        self._u_cat.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=4)
        gold_btn(uc, "  Update Entry  ->", self._do_upd,
                 bg=AMBER, fg=BG()).pack(anchor="w", padx=16, pady=(0, 16))

    def _do_del(self):
        s = self._d_id.get()
        if not s: messagebox.showerror("Error", "Enter an ID."); return
        try:    eid = int(s)
        except: messagebox.showerror("Error", "ID must be a number."); return
        if not messagebox.askyesno("Confirm Delete",
                f"Permanently delete transaction #{eid}?"): return
        try:
            ok = tracker.delete_expense_by_id(eid)
            if ok:
                show_toast(self, f"Deleted transaction #{eid}", RED)
                self._d_id.clear()
            else:
                messagebox.showwarning("Not Found", f"ID #{eid} not found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _do_upd(self):
        id_s  = self._u_id.get()
        amt_s = self._u_amt.get()
        ttl_s = self._u_ttl.get()
        cat_s = self._u_cat.get()
        if not id_s: messagebox.showerror("Error", "Provide an ID."); return
        try:    eid = int(id_s)
        except: messagebox.showerror("Error", "ID must be an integer."); return
        if not any([amt_s, ttl_s, cat_s != "(keep)"]):
            messagebox.showerror("Error", "Fill at least one field."); return
        try:
            if amt_s:
                try:    new_amt = float(amt_s)
                except: messagebox.showerror("Error", "Amount must be a number."); return
                if not tracker.update_expense_amount(eid, new_amt):
                    messagebox.showwarning("Not Found", f"ID #{eid} not found."); return
            if ttl_s and hasattr(tracker, "update_expense_title"):
                tracker.update_expense_title(eid, ttl_s)
            if cat_s != "(keep)" and hasattr(tracker, "update_expense_category"):
                tracker.update_expense_category(eid, cat_s)
            show_toast(self, "Transaction updated")
            for e in (self._u_id, self._u_amt, self._u_ttl): e.clear()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── Monthly Report ────────────────────────────────────────────────────
    def _pg_report(self):
        self._hdr("Monthly Report", "Spending analysis by month")
        outer = tk.Frame(self._main, bg=BG())
        outer.pack(fill="both", expand=True, padx=28, pady=18)

        fb = tk.Frame(outer, bg=CARD(), highlightthickness=1,
                      highlightbackground=BORDER())
        fb.pack(fill="x")
        tk.Frame(fb, bg=GOLD, height=2).pack(fill="x")
        row = tk.Frame(fb, bg=CARD())
        row.pack(fill="x", padx=20, pady=16)
        self._r_month = StyledEntry(row, "MONTH (1-12)")
        self._r_month.set(str(date.today().month))
        self._r_month.pack(side="left", padx=(0, 10))
        self._r_year = StyledEntry(row, "YEAR")
        self._r_year.set(str(date.today().year))
        self._r_year.pack(side="left", padx=(0, 14))
        gold_btn(row, "Generate Report ->", self._do_report).pack(side="left")

        self._rep_area = tk.Frame(outer, bg=BG())
        self._rep_area.pack(fill="both", expand=True, pady=(14, 0))
        self._do_report()

    def _do_report(self):
        for w in self._rep_area.winfo_children(): w.destroy()
        m_s = self._r_month.get()
        y_s = self._r_year.get()
        try:
            m = int(m_s)
            if not 1 <= m <= 12: raise ValueError
        except: messagebox.showerror("Error", "Month must be 1-12."); return
        try:    yr = int(y_s)
        except: yr = date.today().year
        try:    total = tracker.monthly_report_total(m)
        except Exception as e: messagebox.showerror("Error", str(e)); return

        month_name = datetime(2000, m, 1).strftime("%B")

        sc = tk.Frame(self._rep_area, bg=CARD(), highlightthickness=1,
                      highlightbackground=BORDER())
        sc.pack(fill="x", pady=(0, 14))
        tk.Frame(sc, bg=GOLD, height=2).pack(fill="x")
        inn = tk.Frame(sc, bg=CARD())
        inn.pack(fill="x", padx=20, pady=16)
        tk.Label(inn, text=f"{month_name} {yr}",
                 font=("Segoe UI", 10), bg=CARD(), fg=FG3()).pack(anchor="w")
        tk.Label(inn, text=f"Rs.{total:,.2f}",
                 font=("Georgia", 28, "bold"), bg=CARD(), fg=GOLD).pack(anchor="w")
        tk.Label(inn, text="Total expenditure this month",
                 font=("Segoe UI", 9), bg=CARD(), fg=FG3()).pack(anchor="w")

        try:
            rows = tracker.view_expenses_records()
            prefix = f"{yr}-{m:02d}"
            cat_t = {}
            for r in rows:
                if str(r[4]).startswith(prefix):
                    cat_t[r[3]] = cat_t.get(r[3], 0) + r[2]

            if cat_t and total > 0:
                bc = tk.Frame(self._rep_area, bg=CARD(), highlightthickness=1,
                              highlightbackground=BORDER())
                bc.pack(fill="x")
                tk.Label(bc, text="Category Breakdown",
                         font=("Georgia", 12, "bold"), bg=CARD(), fg=FG()).pack(
                    anchor="w", padx=16, pady=(14, 8))
                tk.Frame(bc, bg=BORDER(), height=1).pack(fill="x", padx=16, pady=(0, 8))
                for cat, amt in sorted(cat_t.items(), key=lambda x: -x[1]):
                    pct = amt / total
                    f = tk.Frame(bc, bg=CARD())
                    f.pack(fill="x", padx=16, pady=4)
                    cc = cat_color(cat)
                    top = tk.Frame(f, bg=CARD())
                    top.pack(fill="x")
                    tk.Label(top, text=f"{cat_icon(cat)} {cat}",
                             font=("Segoe UI", 10), bg=CARD(), fg=FG()).pack(side="left")
                    tk.Label(top, text=f"Rs.{amt:,.2f}   {pct*100:.1f}%",
                             font=("Segoe UI", 10, "bold"), bg=CARD(), fg=cc).pack(side="right")
                    bar_bg = tk.Frame(f, bg=BORDER(), height=6)
                    bar_bg.pack(fill="x", pady=(4, 0))
                    def _draw(e=None, p=pct, c=cc, b=bar_bg):
                        b.update_idletasks()
                        w = int(b.winfo_width() * p)
                        tk.Frame(b, bg=c, height=6, width=max(4, w)).place(x=0, y=0)
                    bar_bg.bind("<Configure>", _draw)
                tk.Frame(bc, bg=CARD(), height=14).pack()
        except: pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
