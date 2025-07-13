from flask import Blueprint, Response, render_template_string
from ..services.detector_service import (
    frames,
    start as start_detection,
    stop as stop_detection,
    health as detector_health,
)

bp = Blueprint('detector', __name__)

INDEX_HTML = """
<!doctype html>
<title>WareEye Stream</title>
<h1>Live Pallet Barcode Detection</h1>
<img id=\"feed\" src=\"/video_feed\" width=\"720\"/>
<br>
<button onclick=\"fetch('/start')\">Start</button>
<button onclick=\"fetch('/stop')\">Stop</button>
"""

@bp.route('/')
def index():
    return render_template_string(INDEX_HTML)


def generate():
    yield from frames()


@bp.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/start')
def start():
    start_detection()
    return 'started'


@bp.route('/stop')
def stop():
    stop_detection()
    return 'stopped'


@bp.route('/healthz')
def healthz():
    return detector_health()
