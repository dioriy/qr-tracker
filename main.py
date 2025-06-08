import os
from flask import Flask, request, send_file, abort
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "log.txt")
HTML_FILE = os.path.join(BASE_DIR, "index.html")

@app.route("/log", methods=["POST"])
def log():
    data = request.json
    user_agent = data.get("userAgent", "unknown")
    ip_address = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    combined = f"{ip_address} | {user_agent}"

    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                if combined in f.read():
                    return "Duplicate ignored"
    except Exception as e:
        return str(e)

    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} | {combined}\n")

    return "Logged!"

@app.route("/")
def index():
    if os.path.exists(HTML_FILE):
        return send_file(HTML_FILE)
    else:
        return abort(404)

@app.route("/count")
def count():
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            return f"QR linkini {len(lines)} marta ochishgan ✅"
    except:
        return "0"

# Lokal test uchun
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
