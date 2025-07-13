from flask import Blueprint, Response, render_template, jsonify
from ..services import webcam_service, barcode_service

bp = Blueprint('webcam', __name__)

@bp.route('/')
def index():
    scans = barcode_service.get_all()
    return render_template('index.html', scans=scans)


def generate():
    for frame in webcam_service.frames():
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"


@bp.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/last_scan')
def last_scan():
    ts = barcode_service.get_last_timestamp()
    return jsonify({'lastScannedAt': ts})
