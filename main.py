import os
from flask import Flask, request, send_file, abort, Response
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
    from collections import defaultdict
    import datetime

    stats = defaultdict(int)
    total = 0

    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                if "|" in line:
                    date_str = line.split("|")[0].strip()
                    try:
                        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        date_only = dt.strftime("%Y-%m-%d")
                        stats[date_only] += 1
                        total += 1
                    except:
                        pass
    except FileNotFoundError:
        return "<h3>Hali birorta kirish qayd etilmagan.</h3>"

    # Jadval uchun HTML + CSS
    html = '''
    <html>
    <head>
    <meta charset="UTF-8">
    <title>QR OCHILISHLAR STATISTIKASI</title>
    <style>
        body { 
            background: #f9fafc; 
            font-family: 'Segoe UI', Arial, sans-serif; 
            text-align: center;
            margin: 0; padding: 0;
        }
        .container {
            margin: 40px auto; 
            max-width: 450px;
            background: #fffbe5;
            border-radius: 15px;
            box-shadow: 0 2px 12px #fff9c4, 0 1.5px 8px #ffe082;
            padding: 30px 18px 18px 18px;
        }
        h2 { 
            color: #e6a100; 
            font-size: 1.7em;
            margin-bottom: 16px;
            letter-spacing: 1px;
            font-weight: 700;
            text-shadow: 0 1px 0 #fffde7;
        }
        table { 
            margin: 0 auto 20px auto; 
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: none;
            padding: 12px 9px;
            font-size: 1.12em;
            text-align: center;
        }
        th {
            background: #ffe082;
            color: #b98600;
            font-weight: bold;
            letter-spacing: .5px;
        }
        tr:nth-child(even) td {
            background: #fffde7;
        }
        tr:nth-child(odd) td {
            background: #fff8e1;
        }
        tr:last-child td {
            background: #fff3c4;
            color: #fff;
            font-weight: 700;
            font-size: 1.1em;
            letter-spacing: 1.2px;
            text-shadow: 0 1px 0 #e6a100;
        }
        .total-cell {
            background: #ffeb3b !important;
            color: #a17a00 !important;
            font-weight: bold !important;
            font-size: 1.2em !important;
        }
        .btn-download {
            display: inline-block;
            margin: 16px 0 0 0;
            background: #ffe082;
            color: #b98600;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            transition: background 0.2s;
        }
        .btn-download:hover {
            background: #fffde7;
        }
    </style>
    </head>
    <body>
    <div class="container">
      <h2>QR KOD OCHILISHLARI JADVALI</h2>
      <table>
        <tr>
            <th>Sana</th>
            <th>Ochilishlar soni</th>
        </tr>
    '''
    for date, count in sorted(stats.items()):
        html += f"<tr><td>{date}</td><td>{count}</td></tr>"
    html += f'''
        <tr>
            <td class="total-cell">JAMI</td>
            <td class="total-cell">{total}</td>
        </tr>
      </table>
      <a class="btn-download" href="/download-csv">⬇ Excel/CSV yuklab olish</a>
    </div>
    </body>
    </html>
    '''
    return html

@app.route("/download-csv")
def download_csv():
    from collections import defaultdict
    import datetime

    stats = defaultdict(int)
    total = 0
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                if "|" in line:
                    date_str = line.split("|")[0].strip()
                    try:
                        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        date_only = dt.strftime("%Y-%m-%d")
                        stats[date_only] += 1
                        total += 1
                    except:
                        pass
    except FileNotFoundError:
        return "Sana,Son\n"

    # CSV tayyorlaymiz
    csv_data = "Sana,Ochilishlar soni\n"
    for date, count in sorted(stats.items()):
        csv_data += f"{date},{count}\n"
    csv_data += f"JAMI,{total}\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=qr-statistika.csv"}
    )

@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        try:
            open(LOG_FILE, "w").close()
            message = '''
                <h2 style="color:#e6a100;">Statistika tozalandi! 🔄</h2>
                <p style="font-size:1.3em;">Natijalar 0 ga tenglashtirildi.</p>
                <a href="/count" style="color:#d4af37;font-size:1.1em;">⬅ Jadvalga qaytish</a>
            '''
        except:
            message = "<b>Xatolik! log.txt topilmadi.</b>"
        return f"""
            <html>
            <head><meta charset="UTF-8"></head>
            <body style="text-align:center;padding-top:70px;font-family:Arial">
                {message}
            </body>
            </html>
        """
    else:
        return '''
            <html>
            <head><meta charset="UTF-8"></head>
            <body style="text-align:center;padding-top:70px;font-family:Arial">
                <h2 style="color:#e6a100;">Statistikani tozalash</h2>
                <form method="POST">
                    <button type="submit" style="
                        background:#ffe082;
                        color:#b98600;
                        padding:12px 32px;
                        font-size:1.18em;
                        border:none;
                        border-radius:8px;
                        font-weight:bold;
                        cursor:pointer;
                        margin-top:24px;
                        transition:background 0.2s;">
                        🔄 TOZALASH
                    </button>
                </form>
                <a href="/count" style="display:block;margin-top:30px;color:#d4af37;font-size:1.1em;">⬅ Jadvalga qaytish</a>
            </body>
            </html>
        '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
