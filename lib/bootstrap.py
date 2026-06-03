import importlib.util
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

if getattr(sys, "frozen", False):
    ROOT = os.path.dirname(os.path.abspath(sys.executable))
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIREMENTS = os.path.join(ROOT, "requirements.txt")
MAIN = os.path.join(ROOT, "lib", "main.py")
LOG = os.path.join(ROOT, "bootstrap.log")

PACKAGES = [
    ("customtkinter", "customtkinter"),
    ("CTkToolTip", "CTkToolTip"),
    ("Flask", "flask"),
    ("minecraft-launcher-lib", "minecraft_launcher_lib"),
    ("Pillow", "PIL"),
    ("requests", "requests"),
]

def candidate_pythons():
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python312", "python.exe"),
        r"C:\Program Files\Python312\python.exe",
        r"C:\Program Files (x86)\Python312\python.exe",
        "python",
        "py",
    ]
    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        yield candidate

def run_hidden(command, check=False):
    startupinfo = None
    creationflags = 0
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        creationflags = subprocess.CREATE_NO_WINDOW
    return subprocess.run(
        command,
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
        startupinfo=startupinfo,
        creationflags=creationflags,
    )

def write_log(text):
    try:
        with open(LOG, "a", encoding="utf-8") as file:
            file.write(text + "\n")
    except Exception:
        pass

def find_python():
    for candidate in candidate_pythons():
        command = [candidate, "--version"]
        if candidate == "py":
            command = [candidate, "-3", "--version"]
        try:
            result = run_hidden(command)
            if result.returncode == 0:
                return candidate
        except Exception:
            pass
    return ""

def python_command(python):
    if python == "py":
        return ["py", "-3"]
    return [python]

def pythonw_from_python(python):
    if python == "py":
        return ["pyw", "-3"]
    folder = os.path.dirname(python)
    pythonw = os.path.join(folder, "pythonw.exe")
    if os.path.exists(pythonw):
        return [pythonw]
    return [python]

def install_python():
    try:
        result = run_hidden(["winget", "--version"])
        if result.returncode != 0:
            return False
    except Exception:
        return False
    install = run_hidden(["winget", "install", "--id", "Python.Python.3.12", "-e", "--silent"])
    return install.returncode == 0

def missing_packages(python):
    missing = []
    for package, module in PACKAGES:
        code = f"import importlib.util; raise SystemExit(0 if importlib.util.find_spec({module!r}) else 1)"
        try:
            result = run_hidden(python_command(python) + ["-c", code])
            if result.returncode != 0:
                missing.append(package)
        except Exception:
            missing.append(package)
    return missing

def install_packages(python):
    pip = python_command(python) + ["-m", "pip"]
    run_hidden(pip + ["install", "--upgrade", "pip"])
    result = run_hidden(pip + ["install", "-r", REQUIREMENTS])
    return result.returncode == 0, result.stderr or result.stdout

def start_app(python):
    if not os.path.exists(MAIN):
        messagebox.showerror("Eclipse Client", f"Die Startdatei wurde nicht gefunden:\n{MAIN}")
        return
    env = os.environ.copy()
    for key in list(env.keys()):
        if key.startswith("_PYI") or key in ["PYTHONHOME", "PYTHONPATH", "TCL_LIBRARY", "TK_LIBRARY"]:
            env.pop(key, None)
    log_path = os.path.join(ROOT, "eclipseclientlog.txt")
    log_file = open(log_path, "a", encoding="utf-8", errors="replace")
    write_log(f"LAUNCH={' '.join(python_command(python) + [MAIN])}")
    subprocess.Popen(
        python_command(python) + [MAIN],
        cwd=ROOT,
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )

def set_status(root, label, text):
    write_log(text)
    label.configure(text=text)
    root.update()

def main():
    root = tk.Tk()
    root.title("Eclipse Client Setup")
    root.geometry("420x140")
    root.resizable(False, False)
    root.lift()
    root.attributes("-topmost", True)
    root.after(1000, lambda: root.attributes("-topmost", False))
    label = tk.Label(root, text="Prüfe Eclipse Client...", font=("Segoe UI", 11), wraplength=380)
    label.pack(expand=True, padx=20, pady=20)

    write_log(f"ROOT={ROOT}")
    write_log(f"MAIN={MAIN}")
    write_log(f"REQUIREMENTS={REQUIREMENTS}")

    set_status(root, label, "Suche Python...")
    python = find_python()
    write_log(f"PYTHON={python}")
    installed_something = False

    if python == "":
        if not messagebox.askyesno("Eclipse Client", "Python wurde nicht gefunden. Soll Python 3.12 installiert werden?"):
            return
        if not install_python():
            messagebox.showerror("Eclipse Client", "Python konnte nicht automatisch installiert werden.")
            return
        installed_something = True
        python = find_python()
        if python == "":
            messagebox.showerror("Eclipse Client", "Python wurde installiert, aber noch nicht gefunden. Bitte starte den PC neu oder installiere Python manuell.")
            return

    set_status(root, label, "Prüfe Bibliotheken...")
    missing = missing_packages(python)
    write_log("MISSING=" + ", ".join(missing))
    if missing:
        text = "Es fehlen Bibliotheken:\n\n" + "\n".join(missing) + "\n\nSoll alles installiert werden?"
        if not messagebox.askyesno("Eclipse Client", text):
            return
        set_status(root, label, "Installiere Bibliotheken...")
        ok, output = install_packages(python)
        if not ok:
            messagebox.showerror("Eclipse Client", "Bibliotheken konnten nicht installiert werden.\n\n" + output[-1200:])
            return
        installed_something = True

    if installed_something:
        if messagebox.askyesno("Eclipse Client", "Alles wurde installiert. Möchtest du Eclipse Client jetzt starten?"):
            set_status(root, label, "Starte Eclipse Client...")
            start_app(python)
    else:
        set_status(root, label, "Starte Eclipse Client...")
        start_app(python)
    root.destroy()

if __name__ == "__main__":
    main()
