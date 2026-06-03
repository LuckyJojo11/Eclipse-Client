import logging
import threading
import webbrowser
from flask import Flask, request
import minecraft_launcher_lib
import time
import socket

CLIENT_ID = "efd15909-62ac-4269-a0c6-3a35e41d1f19"
REDIRECT_URI = "http://localhost:4712/callback"

app = Flask(__name__)

logging.getLogger("werkzeug").setLevel(logging.ERROR)

login_result = {
    "done": False,
    "account": None,
    "error": None
}

login_data = None
server_started = False
server_lock = threading.Lock()
login_lock = threading.Lock()


@app.route("/callback")
def callback():
    global login_data

    try:
        if login_data is None:
            raise RuntimeError("No login request is active")

        auth_code = minecraft_launcher_lib.microsoft_account.parse_auth_code_url(
            request.url,
            login_data[1]
        )

        account_information = minecraft_launcher_lib.microsoft_account.complete_login(
            CLIENT_ID,
            None,
            REDIRECT_URI,
            auth_code,
            login_data[2]
        )

        #print("ACCOUNT_INFORMATION:", account_information)
        #print("ACCOUNT_KEYS:", account_information.keys() if isinstance(account_information, dict) else "not a dict")

        if not isinstance(account_information, dict):
            raise TypeError(f"Login result is not a dict: {type(account_information)}")

        required_keys = ["name", "id", "access_token"]
        missing = [key for key in required_keys if key not in account_information]
        if missing:
            raise KeyError(f"Missing keys in login result: {missing}. Full result: {account_information}")

        login_result["done"] = True
        login_result["account"] = account_information

        return """
        <img src="lib/images/icon.ico"/>
        <h1>Login erfolgreich</h1>
        <p>Du kannst dieses Fenster jetzt schließen und zum Launcher zurückkehren.</p>
        """
    except Exception as e:
        login_result["done"] = True
        login_result["error"] = str(e)

        return f"""
        <h1>Login fehlgeschlagen</h1>
        <p>{e}</p>
        """


def run_flask():
    app.run(host="127.0.0.1", port=4712, debug=False, use_reloader=False, threaded=True)

def ensure_server_running():
    global server_started
    with server_lock:
        if server_started:
            return
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        server_started = True
        time.sleep(0.4)


def begin_login():
    global login_data

    login_result["done"] = False
    login_result["account"] = None
    login_result["error"] = None

    login_data = minecraft_launcher_lib.microsoft_account.get_secure_login_data(
        CLIENT_ID,
        REDIRECT_URI
    )

    auth_url = login_data[0]

    ensure_server_running()
    webbrowser.open(auth_url)


def get_login_result():
    return login_result

def login(timeout=180):
    if not login_lock.acquire(blocking=False):
        return False
    try:
        begin_login()
        start = time.time()

        while True:
            result = get_login_result()

            if result["done"]:
                if result["error"]:
                    #print("Fehler beim Login:")
                    #print(result["error"])
                    return False
                else:
                    account = result["account"]
                    #print("Login erfolgreich!")
                    #print("Name:", account["name"])
                    #print("UUID:", account["id"])
                    #print("Token:", account["access_token"])
                return account

            if time.time() - start > timeout:
                return False

            if not internet():
                return False
            time.sleep(1)
    finally:
        login_lock.release()
        
def refresh(token):
    if not token:
        return False
    new_id = minecraft_launcher_lib.microsoft_account.complete_refresh(
        CLIENT_ID,
        client_secret="",
        redirect_uri=REDIRECT_URI,
        refresh_token=token
    )
    return new_id

def internet(host="login.live.com", port=443, timeout=3):
    try:
        connection = socket.create_connection((host, port), timeout=timeout)
        connection.close()
        return True
    except socket.error as ex:
        return False
