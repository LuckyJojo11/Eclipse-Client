import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
import zipfile
from tkinter import messagebox
from urllib.request import Request, urlopen

if getattr(sys, "frozen", False):
    ROOT = os.path.dirname(os.path.abspath(sys.executable))
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCE_DIR = os.path.join(ROOT, "lib", "applicationresources")
REQUIREMENTS = os.path.join(RESOURCE_DIR, "requirements.txt")
MAIN = os.path.join(ROOT, "lib", "main.py")
LOG = os.path.join(RESOURCE_DIR, "bootstrap.log")
VERSION_FILE = os.path.join(RESOURCE_DIR, ".eclipse_client_version")
SETUP_FILE = os.path.join(RESOURCE_DIR, ".setup_done")
APP_VERSION = "v1.0.1"
GITHUB_API = "https://api.github.com/repos/LuckyJojo11/Eclipse-Client/releases/latest"
USER_AGENT = "EclipseClientBootstrap/1.0"

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
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as file:
            file.write(text + "\n")
    except Exception:
        pass

def request_json(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))

def download_file(url, destination):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        with open(destination, "wb") as file:
            shutil.copyfileobj(response, file)

def source_is_missing():
    return not os.path.exists(MAIN) or not os.path.exists(REQUIREMENTS)

def local_version():
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r", encoding="utf-8") as file:
                version = file.read().strip()
                if version:
                    return version
    except Exception:
        pass
    return APP_VERSION

def save_local_version(version):
    try:
        with open(VERSION_FILE, "w", encoding="utf-8") as file:
            file.write(version)
    except Exception:
        pass

def latest_release():
    data = request_json(GITHUB_API)
    return {
        "tag": data.get("tag_name", ""),
        "zip": data.get("zipball_url", "")
    }

def should_skip_source_file(relative):
    relative = relative.replace("\\", "/").strip("/")
    if relative == "":
        return True
    blocked_names = {
        "Eclipse Client.exe",
        "Eclipse Client.spec",
        "bootstrap.log",
        "eclipseclientlog.txt"
    }
    blocked_folders = [
        ".git/",
        ".mixin.out/",
        "build/",
        "build_deps/",
        "build_venv/",
        "config/",
        "dist/",
        "instances/",
        "logs/",
        "lib/__pycache__/",
        "lib/files/",
        "lib/logs/"
    ]
    blocked_resource_files = {
        "lib/applicationresources/.eclipse_client_version",
        "lib/applicationresources/.setup_done",
        "lib/applicationresources/bootstrap.log",
        "lib/applicationresources/eclipseclientlog.txt"
    }
    if relative in blocked_names:
        return True
    if relative in blocked_resource_files:
        return True
    if relative.startswith("lib/files/") and relative != "lib/files/.gitkeep":
        return True
    for folder in blocked_folders:
        if relative.startswith(folder):
            return True
    return False

def install_source_zip(zip_path):
    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            parts = member.filename.split("/", 1)
            if len(parts) != 2:
                continue
            relative = parts[1]
            if should_skip_source_file(relative):
                continue
            destination = os.path.join(ROOT, relative.replace("/", os.sep))
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with archive.open(member) as source, open(destination, "wb") as target:
                shutil.copyfileobj(source, target)

def download_latest_source(release):
    if release.get("zip", "") == "":
        raise RuntimeError("GitHub release has no source zip.")
    with tempfile.TemporaryDirectory() as temp:
        zip_path = os.path.join(temp, "source.zip")
        download_file(release["zip"], zip_path)
        install_source_zip(zip_path)
    if release.get("tag", "") != "":
        save_local_version(release["tag"])

def check_source_update(root, label):
    try:
        set_status(root, label, "Checking GitHub Release...")
        release = latest_release()
        latest = release.get("tag", "")
        current = local_version()
        write_log(f"LOCAL_VERSION={current}")
        write_log(f"LATEST_VERSION={latest}")

        if source_is_missing():
            if not messagebox.askyesno("Eclipse Client", "Source files are missing. Do you want to download the latest release from GitHub?"):
                return False
            set_status(root, label, "Downloading Eclipse Client...")
            download_latest_source(release)
            return True

        if latest != "" and latest != current:
            text = f"A new Eclipse Client release is available:\n\nCurrent: {current}\nLatest: {latest}\n\nDo you want to update now?"
            if messagebox.askyesno("Eclipse Client Update", text):
                set_status(root, label, "Updating Eclipse Client...")
                download_latest_source(release)
                return True
        return True
    except Exception as e:
        write_log(f"UPDATE_CHECK_FAILED={e}")
        if source_is_missing():
            messagebox.showerror("Eclipse Client", "Source files are missing and the latest release could not be downloaded.\n\n" + str(e))
            return False
        return True

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

def shortcut_target():
    if getattr(sys, "frozen", False):
        return sys.executable
    exe = os.path.join(ROOT, "Eclipse Client.exe")
    if os.path.exists(exe):
        return exe
    vbs = os.path.join(RESOURCE_DIR, "Eclipse Client.vbs")
    if os.path.exists(vbs):
        return vbs
    return os.path.join(ROOT, "lib", "bootstrap.py")

def create_shortcut(path, target):
    icon = os.path.join(ROOT, "lib", "images", "icon.ico")
    working_directory = ROOT
    script = (
        "$shell = New-Object -ComObject WScript.Shell; "
        f"$shortcut = $shell.CreateShortcut('{path}'); "
        f"$shortcut.TargetPath = '{target}'; "
        f"$shortcut.WorkingDirectory = '{working_directory}'; "
        f"$shortcut.IconLocation = '{icon}'; "
        "$shortcut.Save()"
    )
    run_hidden(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script])

def create_shortcuts(desktop, start_menu):
    target = shortcut_target()
    if desktop:
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        create_shortcut(os.path.join(desktop_dir, "Eclipse Client.lnk"), target)
    if start_menu:
        start_menu_dir = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs")
        if start_menu_dir.strip():
            os.makedirs(start_menu_dir, exist_ok=True)
            create_shortcut(os.path.join(start_menu_dir, "Eclipse Client.lnk"), target)

def setup_was_done():
    return os.path.exists(SETUP_FILE)

def mark_setup_done():
    try:
        os.makedirs(os.path.dirname(SETUP_FILE), exist_ok=True)
        with open(SETUP_FILE, "w", encoding="utf-8") as file:
            file.write(APP_VERSION)
    except Exception:
        pass

def ask_first_start_options(root, label):
    if setup_was_done():
        return

    dialog = tk.Toplevel(root)
    dialog.title("Eclipse Client Installation")
    dialog.geometry("420x230")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()

    desktop_var = tk.BooleanVar(value=True)
    start_menu_var = tk.BooleanVar(value=True)
    result = {"ok": False}

    title = tk.Label(dialog, text="Finish Eclipse Client setup", font=("Segoe UI", 15, "bold"))
    title.pack(anchor="w", padx=22, pady=(18, 6))

    text = tk.Label(dialog, text="Choose where shortcuts should be created.", font=("Segoe UI", 10), wraplength=360, justify="left")
    text.pack(anchor="w", padx=22, pady=(0, 12))

    desktop_check = tk.Checkbutton(dialog, text="Create desktop shortcut", variable=desktop_var, font=("Segoe UI", 10))
    desktop_check.pack(anchor="w", padx=22, pady=4)

    start_menu_check = tk.Checkbutton(dialog, text="Create Start Menu entry", variable=start_menu_var, font=("Segoe UI", 10))
    start_menu_check.pack(anchor="w", padx=22, pady=4)

    buttons = tk.Frame(dialog)
    buttons.pack(fill="x", padx=22, pady=(18, 0))

    def continue_setup():
        result["ok"] = True
        dialog.destroy()

    def skip_setup():
        result["ok"] = False
        dialog.destroy()

    tk.Button(buttons, text="Skip", width=12, command=skip_setup).pack(side="right", padx=(8, 0))
    tk.Button(buttons, text="Continue", width=12, command=continue_setup).pack(side="right")

    root.wait_window(dialog)
    if result["ok"]:
        set_status(root, label, "Creating shortcuts...")
        create_shortcuts(desktop_var.get(), start_menu_var.get())
    mark_setup_done()

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
        messagebox.showerror("Eclipse Client", f"Starting File not found:\n{MAIN}")
        return
    env = os.environ.copy()
    for key in list(env.keys()):
        if key.startswith("_PYI") or key in ["PYTHONHOME", "PYTHONPATH", "TCL_LIBRARY", "TK_LIBRARY"]:
            env.pop(key, None)
    log_path = os.path.join(RESOURCE_DIR, "eclipseclientlog.txt")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
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
    root.title("Eclipse Client Installer")
    root.geometry("520x260")
    root.resizable(False, False)
    root.configure(bg="#f4f6f8")
    root.lift()
    root.attributes("-topmost", True)
    root.after(1000, lambda: root.attributes("-topmost", False))

    container = tk.Frame(root, bg="#f4f6f8")
    container.pack(fill="both", expand=True, padx=26, pady=22)

    title = tk.Label(container, text="Eclipse Client", font=("Segoe UI", 20, "bold"), bg="#f4f6f8", fg="#1f2933")
    title.pack(anchor="w")

    subtitle = tk.Label(container, text="Setup, update and launcher bootstrap", font=("Segoe UI", 10), bg="#f4f6f8", fg="#52606d")
    subtitle.pack(anchor="w", pady=(0, 20))

    panel = tk.Frame(container, bg="white", highlightbackground="#d9e2ec", highlightthickness=1)
    panel.pack(fill="both", expand=True)

    label = tk.Label(panel, text="Checking Eclipse Client...", font=("Segoe UI", 11), wraplength=420, bg="white", fg="#1f2933", justify="left")
    label.pack(anchor="w", padx=18, pady=(20, 10))

    note = tk.Label(panel, text="Missing files, updates, Python and required libraries are checked automatically.", font=("Segoe UI", 9), wraplength=420, bg="white", fg="#697386", justify="left")
    note.pack(anchor="w", padx=18, pady=(0, 12))

    write_log(f"ROOT={ROOT}")
    write_log(f"RESOURCE_DIR={RESOURCE_DIR}")
    write_log(f"MAIN={MAIN}")
    write_log(f"REQUIREMENTS={REQUIREMENTS}")

    if not check_source_update(root, label):
        root.destroy()
        return

    ask_first_start_options(root, label)

    set_status(root, label, "Searching Python...")
    python = find_python()
    write_log(f"PYTHON={python}")
    installed_something = False

    if python == "":
        if not messagebox.askyesno("Eclipse Client", "Can't fint Python. Do you want to Install Python 3.12?"):
            return
        if not install_python():
            messagebox.showerror("Eclipse Client", "Failed to install Python")
            return
        installed_something = True
        python = find_python()
        if python == "":
            messagebox.showerror("Eclipse Client", "Python finished Installing but we can't find it. Try to restart your PC and/or install Python manualy")
            return

    set_status(root, label, "Scanning Python Libarys")
    missing = missing_packages(python)
    write_log("MISSING=" + ", ".join(missing))
    if missing:
        text = "There are missing Python Libarys:\n\n" + "\n".join(missing) + "\n\nDo you want to Install them?"
        if not messagebox.askyesno("Eclipse Client", text):
            return
        set_status(root, label, "Installing Python Libarys")
        ok, output = install_packages(python)
        if not ok:
            messagebox.showerror("Eclipse Client", "Failed to Install Python Libarys:\n\n" + output[-1200:])
            return
        installed_something = True

    if installed_something:
        if messagebox.askyesno("Eclipse Client", "Installations Done. Do you want to run \"Eclipse Client\" now?"):
            set_status(root, label, "Starting Eclipse Client...")
            start_app(python)
    else:
        set_status(root, label, "Starting Eclipse Client...")
        start_app(python)
    root.destroy()

if __name__ == "__main__":
    main()
