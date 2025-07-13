from flask import Flask, Response, render_template_string

from services.detector_service import (
    frames,
    start as start_detection,
    stop as stop_detection,
    health as detector_health,
)

app = Flask(__name__)

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


# Stream video frames from the detector service
def generate():
    yield from frames()

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/start")
def start():
    start_detection()
    return "started"

@app.route("/stop")
def stop():
    stop_detection()
    return "stopped"

@app.route("/healthz")
def healthz():
    return detector_health()

if __name__ == "__main__":
    start_detection()
    app.run(host="0.0.0.0", port=5000)
