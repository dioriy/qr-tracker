from flask import Flask, request, send_file
from datetime import datetime

app = Flask(__name__)

@app.route("/log", methods=["POST"])
def log():
    data = request.json
    user_agent = data.get("userAgent", "unknown")
    ip_address = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    combined = f"{ip_address} | {user_agent}"

    try:
        with open("log.txt", "r") as f:
            if combined in f.read():
                return "Duplicate ignored"
    except:
        pass

    with open("log.txt", "a") as f:
        f.write(f"{timestamp} | {combined}\n")

    return "Logged!"

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/count")
def count():
    try:
        with open("log.txt", "r") as f:
            lines = f.readlines()
            return f"QR linkini {len(lines)} marta ochishgan ✅"
    except:
        return "0"

# 🧠 Eng muhim qism:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
