"""
Keep Alive Module for Render Web Service
Creates a simple web server to keep the bot running 24/7 with UptimeRobot
"""

from flask import Flask
from threading import Thread
import logging

# Disable Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    """Health check endpoint"""
    return """
    <html>
        <head>
            <title>Kingdom-77 Bot Status</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    text-align: center;
                    background: rgba(255,255,255,0.1);
                    padding: 50px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                }
                h1 { 
                    margin: 0; 
                    font-size: 3em;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                p { 
                    font-size: 1.3em; 
                    margin-top: 15px;
                }
                .status { 
                    display: inline-block;
                    width: 14px;
                    height: 14px;
                    background: #4ade80;
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                    box-shadow: 0 0 10px #4ade80;
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.6; transform: scale(1.1); }
                }
                .footer {
                    margin-top: 30px;
                    font-size: 0.9em;
                    opacity: 0.8;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Kingdom-77 Bot</h1>
                <p><span class="status"></span> Bot is Running!</p>
                <p class="footer">Translation Bot • 24/7 Uptime • v2.8</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Simple health check for monitoring services"""
    return {"status": "ok", "bot": "Kingdom-77", "version": "2.8", "running": True}, 200

@app.route('/ping')
def ping():
    """Ping endpoint for UptimeRobot"""
    return "pong", 200

def run():
    """Run the Flask server"""
    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        print(f"❌ Error starting keep-alive server: {e}")

def keep_alive():
    """Start the keep-alive server in a separate thread"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("✅ Keep-alive server started on port 8080")
