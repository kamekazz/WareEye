import os
import time
from io import BytesIO
from dotenv import load_dotenv
from flask import Flask, Response, render_template_string

from detector import BarcodeDetector

load_dotenv()

CAMERA_IP = os.getenv("CAMERA_IP", "192.168.1.163")
CAMERA_PASS = os.getenv("CAMERA_PASS", "")
STREAM_URL = f"rtsp://admin:{CAMERA_PASS}@{CAMERA_IP}:554/h264Preview_01_main"

app = Flask(__name__)

detector = BarcodeDetector(STREAM_URL)

INDEX_HTML = """
<!doctype html>
<title>WareEye Stream</title>
<h1>Live Pallet Barcode Detection</h1>
<img id="feed" src="/video_feed" width="720"/>
<br>
<button onclick="fetch('/start')">Start</button>
<button onclick="fetch('/stop')">Stop</button>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


def generate():
    while True:
        frame = detector.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/start")
def start():
    if not detector.is_alive():
        detector.start()
    return "started"

@app.route("/stop")
def stop():
    detector.stop()
    return "stopped"

@app.route("/healthz")
def healthz():
    status = "ok" if detector.is_alive() else "detector stopped"
    return status

if __name__ == "__main__":
    detector.start()
    app.run(host="0.0.0.0", port=5000)
