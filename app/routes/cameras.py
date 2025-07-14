from flask import Blueprint, render_template, request, redirect, url_for, Response, jsonify
from ..services import camera_service, ip_camera_service, barcode_service

bp = Blueprint('cameras', __name__, url_prefix='/cameras')

@bp.route('/')
def list_cameras():
    cameras = camera_service.get_all()
    return render_template('cameras/list.html', cameras=cameras)

@bp.route('/new')
def new_camera_form():
    return render_template('cameras/form.html', camera=None, action=url_for('cameras.create_camera'))

@bp.route('/', methods=['POST'])
def create_camera():
    # Treat missing checkbox value as False when creating the camera
    scanning = request.form.get('scanning') is not None
    camera_service.create(
        request.form.get('name', ''),
        request.form.get('zone', ''),
        request.form.get('ip_address', ''),
        request.form.get('password', ''),
        scanning,
    )
    return redirect(url_for('cameras.list_cameras'))

@bp.route('/<int:camera_id>/edit')
def edit_camera_form(camera_id: int):
    camera = camera_service.get(camera_id)
    if not camera:
        return 'Camera not found', 404
    return render_template('cameras/form.html', camera=camera, action=url_for('cameras.update_camera', camera_id=camera_id))

@bp.route('/<int:camera_id>', methods=['POST'])
def update_camera(camera_id: int):
    # Checkbox not present when unchecked, so default to False
    scanning = request.form.get('scanning') is not None
    camera_service.update(
        camera_id,
        request.form.get('name', ''),
        request.form.get('zone', ''),
        request.form.get('ip_address', ''),
        request.form.get('password', ''),
        scanning,
    )
    return redirect(url_for('cameras.list_cameras'))

@bp.route('/<int:camera_id>/delete', methods=['POST'])
def delete_camera(camera_id: int):
    camera_service.delete(camera_id)
    return redirect(url_for('cameras.list_cameras'))


@bp.route('/<int:camera_id>/view')
def view_camera(camera_id: int):
    """Render a page displaying the camera stream."""
    camera = camera_service.get(camera_id)
    if not camera:
        return 'Camera not found', 404
    scans = barcode_service.get_all()
    last_timestamp = barcode_service.get_last_timestamp()
    return render_template('cameras/view.html', camera=camera, scans=scans, last_timestamp=last_timestamp)


@bp.route('/<int:camera_id>/toggle_scanning', methods=['POST'])
def toggle_scanning(camera_id: int):
    """Toggle the scanning state for the given camera."""
    new_state = camera_service.toggle_scanning(camera_id)
    if new_state is None:
        return 'Camera not found', 404
    return redirect(url_for('cameras.view_camera', camera_id=camera_id))


@bp.route('/<int:camera_id>/start_scan', methods=['POST'])
def start_scan(camera_id: int):
    """Start scanning for the specified camera."""
    camera = camera_service.get(camera_id)
    if not camera:
        return 'Camera not found', 404
    ip_camera_service.start_scanning(camera_id, camera['url'])
    return ('', 204)


@bp.route('/<int:camera_id>/stop_scan', methods=['POST'])
def stop_scan(camera_id: int):
    """Stop scanning for the specified camera."""
    ip_camera_service.stop_scanning(camera_id)
    return ('', 204)


@bp.route('/last_scan_timestamp')
def last_scan_timestamp():
    """Return the timestamp of the most recent scan."""
    return jsonify(timestamp=barcode_service.get_last_timestamp())


def _stream_generator(url: str):
    for frame in ip_camera_service.frames(url):
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"


@bp.route('/<int:camera_id>/video_feed')
def video_feed(camera_id: int):
    camera = camera_service.get(camera_id)
    if not camera:
        return 'Camera not found', 404
    return Response(_stream_generator(camera['url']), mimetype='multipart/x-mixed-replace; boundary=frame')
