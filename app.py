from flask import (
    Flask,
    Response,
    render_template_string,
    render_template,
    request,
    redirect,
    url_for,
)

from services.detector_service import (
    frames,
    start as start_detection,
    stop as stop_detection,
    health as detector_health,
)
from services import camera_service

camera_service.init_db()

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


# Camera Management Routes

@app.route("/cameras")
def list_cameras():
    cameras = camera_service.get_all()
    return render_template("cameras.html", cameras=cameras)


@app.route("/cameras/new")
def new_camera_form():
    return render_template(
        "camera_form.html", camera=None, action=url_for("create_camera")
    )


@app.route("/cameras", methods=["POST"])
def create_camera():
    camera_service.create(
        request.form.get("name", ""),
        request.form.get("zone", ""),
        request.form.get("ip_address", ""),
        request.form.get("url", ""),
        request.form.get("password", ""),
    )
    return redirect(url_for("list_cameras"))


@app.route("/cameras/<int:camera_id>/edit")
def edit_camera_form(camera_id: int):
    camera = camera_service.get(camera_id)
    if not camera:
        return "Camera not found", 404
    return render_template(
        "camera_form.html",
        camera=camera,
        action=url_for("update_camera", camera_id=camera_id),
    )


@app.route("/cameras/<int:camera_id>", methods=["POST"])
def update_camera(camera_id: int):
    camera_service.update(
        camera_id,
        request.form.get("name", ""),
        request.form.get("zone", ""),
        request.form.get("ip_address", ""),
        request.form.get("url", ""),
        request.form.get("password", ""),
    )
    return redirect(url_for("list_cameras"))


@app.route("/cameras/<int:camera_id>/delete", methods=["POST"])
def delete_camera(camera_id: int):
    camera_service.delete(camera_id)
    return redirect(url_for("list_cameras"))

if __name__ == "__main__":
    start_detection()
    app.run(host="0.0.0.0", port=5000)
