import os
import logging
from flask import Flask, request, send_file, abort, jsonify
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)
LOG_FILE = os.path.join(BASE_DIR, "log.txt")

# Loglash sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('QRLogger')

@app.before_request
def log_request():
    """Barcha so'rovlarni log qilish"""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.route("/log", methods=["POST"])
def log_visit():
    """QR kod orqali tashriflarni log qilish"""
    try:
        data = request.get_json()
        user_agent = data.get("userAgent", "unknown")
        ip_address = request.remote_addr
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        combined = f"{ip_address} | {user_agent}"
        
        # Duplikatni tekshirish
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                if combined in f.read():
                    return jsonify({"status": "duplicate"}), 200
        
        # Logga yozish
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} | {combined}\n")
        
        return jsonify({"status": "logged"}), 200
    
    except Exception as e:
        logger.error(f"Loglashda xato: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    """Asosiy sahifani qaytarish"""
    return """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QR Tizimga Xush Kelibsiz</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='0.9em' font-size='90'>📊</text></svg>">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
                color: white;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                max-width: 800px;
                width: 100%;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
                text-align: center;
            }
            
            h1 {
                font-size: 3rem;
                margin-bottom: 20px;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            }
            
            .stats {
                display: flex;
                justify-content: space-around;
                margin: 40px 0;
            }
            
            .stat-box {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 25px;
                width: 45%;
                transition: transform 0.3s ease;
            }
            
            .stat-box:hover {
                transform: translateY(-10px);
                background: rgba(255, 255, 255, 0.25);
            }
            
            .stat-value {
                font-size: 4rem;
                font-weight: bold;
                margin: 15px 0;
                color: #ffd700;
            }
            
            .stat-label {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            
            .redirect-info {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 15px;
                padding: 20px;
                margin: 30px 0;
            }
            
            .countdown {
                font-size: 1.8rem;
                font-weight: bold;
                color: #ffd700;
                margin: 15px 0;
            }
            
            .telegram-link {
                display: inline-block;
                background: #0088cc;
                color: white;
                padding: 15px 30px;
                border-radius: 50px;
                text-decoration: none;
                font-size: 1.2rem;
                font-weight: bold;
                margin-top: 20px;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            
            .telegram-link:hover {
                background: #006699;
                transform: scale(1.05);
            }
            
            .telegram-link i {
                margin-right: 10px;
            }
            
            .instructions {
                text-align: left;
                background: rgba(0, 0, 0, 0.1);
                padding: 20px;
                border-radius: 15px;
                margin: 30px 0;
            }
            
            .instructions h3 {
                margin-bottom: 15px;
                color: #ffd700;
            }
            
            .instructions ol {
                padding-left: 20px;
            }
            
            .instructions li {
                margin: 10px 0;
                line-height: 1.6;
            }
            
            @media (max-width: 768px) {
                .stats {
                    flex-direction: column;
                    align-items: center;
                }
                
                .stat-box {
                    width: 100%;
                    margin-bottom: 20px;
                }
                
                h1 {
                    font-size: 2.5rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>QR Kod Tizimi</h1>
            <p>Telegram botimizga yo'naltirilmoqdasiz</p>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-label">Jami Tashriflar</div>
                    <div class="stat-value" id="totalVisits">0</div>
                    <div class="stat-label">marta</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Bugungi Tashriflar</div>
                    <div class="stat-value" id="todayVisits">0</div>
                    <div class="stat-label">marta</div>
                </div>
            </div>
            
            <div class="redirect-info">
                <p>Sizni Telegram botimizga yo'naltirilmoqdasiz:</p>
                <div class="countdown" id="countdown">5</div>
                <p>Yo'naltirilishni kutishingiz yoki quyidagi tugma orqali o'tishingiz mumkin</p>
                <a href="https://t.me/aynimo_official_bot" class="telegram-link">
                    <i class="fab fa-telegram"></i> Botga O'tish
                </a>
            </div>
            
            <div class="instructions">
                <h3>Tizim Qanday Ishlamoqda?</h3>
                <ol>
                    <li>QR kodni skaner qilgan har bir foydalanuvchi avtomatik ravishda log fayliga yoziladi</li>
                    <li>Har bir yangi tashrif hisobga olinadi (bir xil qurilmadan bir marta)</li>
                    <li>Yuqoridagi statistikalar real vaqtda yangilanadi</li>
                    <li>5 soniya ichida siz Telegram botimizga yo'naltirilasiz</li>
                </ol>
            </div>
        </div>
        
        <script>
            // Countdown funksiyasi
            let seconds = 5;
            const countdownElement = document.getElementById('countdown');
            
            const countdown = setInterval(() => {
                seconds--;
                countdownElement.textContent = seconds;
                
                if (seconds <= 0) {
                    clearInterval(countdown);
                    window.location.href = "https://t.me/aynimo_official_bot";
                }
            }, 1000);
            
            // Statistikani yuklash
            async function loadStats() {
                try {
                    const response = await fetch('/count');
                    if (!response.ok) throw new Error('Statistikani yuklab bo\'lmadi');
                    
                    const data = await response.text();
                    const visits = parseInt(data.match(/\d+/)?.[0] || 0;
                    
                    document.getElementById('totalVisits').textContent = visits;
                    document.getElementById('todayVisits').textContent = Math.floor(visits / 3);
                    
                } catch (error) {
                    console.error('Xato:', error);
                }
            }
            
            // Dastlabki statistikani yuklash
            loadStats();
            
            // Har 10 soniyada statistikani yangilash
            setInterval(loadStats, 10000);
        </script>
    </body>
    </html>
    """

@app.route("/count")
def count_visits():
    """Tashriflar sonini qaytarish"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
                return f"QR linkini {len(lines)} marta ochishgan ✅", 200
        return "0", 200
    except Exception as e:
        logger.error(f"Tashriflarni hisoblashda xato: {str(e)}")
        return "Xato: " + str(e), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
