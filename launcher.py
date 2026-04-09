import subprocess
import threading
import webbrowser
import time
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def run_web():
    """Start the Flask web server in background."""
    app_path = os.path.join(_HERE, "app.py")
    subprocess.Popen(
        [sys.executable, app_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=_HERE
    )


def run_desktop():
    """Start the tkinter desktop app."""
    import tkinter as tk
    sys.path.insert(0, _HERE)

    root = tk.Tk()
    root.title("Expense Ledger Launcher")
    root.geometry("400x220")
    root.configure(bg="#0d1117")
    root.resizable(False, False)

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"400x220+{(sw-400)//2}+{(sh-220)//2}")

    tk.Label(root, text="Rs.", font=("Georgia", 28, "bold"),
             bg="#0d1117", fg="#c9a84c").pack(pady=(20, 4))
    tk.Label(root, text="EXPENSE LEDGER",
             font=("Georgia", 13, "bold"), bg="#0d1117", fg="#e8eaf6").pack()
    tk.Label(root, text="Choose how to launch",
             font=("Segoe UI", 9), bg="#0d1117", fg="#4a5568").pack(pady=(4, 16))

    btn_frame = tk.Frame(root, bg="#0d1117")
    btn_frame.pack()

    def launch_desktop():
        root.destroy()
        import project
        app = project.App()
        app.mainloop()

    def launch_web():
        root.destroy()
        webbrowser.open("https://expense-ledger.onrender.com/login")

    def launch_both():
        root.destroy()
        wt = threading.Thread(target=run_web, daemon=True)
        wt.start()
        time.sleep(1)
        import project
        app = project.App()
        app.mainloop()

    for text, cmd, color in [
        ("🖥  Desktop App",       launch_desktop, "#1a2035"),
        ("🌐  Web App (Browser)", launch_web,     "#1a2035"),
        ("⚡  Both Together",     launch_both,    "#c9a84c"),
    ]:
        fg = "#c9a84c" if color == "#1a2035" else "#0d1117"
        btn = tk.Button(btn_frame, text=text, command=cmd,
                        bg=color, fg=fg, font=("Segoe UI", 10, "bold"),
                        relief="flat", padx=20, pady=8, cursor="hand2",
                        width=22)
        btn.pack(side="left", padx=6)

    root.mainloop()


if __name__ == "__main__":
    run_desktop()