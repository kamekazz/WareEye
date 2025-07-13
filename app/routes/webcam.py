from flask import Blueprint, Response, render_template
from ..services import webcam_service

bp = Blueprint('webcam', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


def generate():
    for frame in webcam_service.frames():
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"


@bp.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
