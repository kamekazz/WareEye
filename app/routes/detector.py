from flask import Blueprint, Response, render_template
from ..services.detector_service import (
    frames,
    start as start_detection,
    stop as stop_detection,
    health as detector_health,
)

bp = Blueprint('detector', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


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
