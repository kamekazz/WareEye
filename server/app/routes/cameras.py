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
    camera_service.create(
        request.form.get('name', ''),
        request.form.get('zone', ''),
        request.form.get('ip_address', ''),
        request.form.get('password', ''),
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
    camera_service.update(
        camera_id,
        request.form.get('name', ''),
        request.form.get('zone', ''),
        request.form.get('ip_address', ''),
        request.form.get('password', ''),
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
    return render_template('cameras/view.html', camera=camera, scans=scans)




def _stream_generator(url: str):
    for frame in ip_camera_service.frames(url):
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"


@bp.route('/<int:camera_id>/video_feed')
def video_feed(camera_id: int):
    camera = camera_service.get(camera_id)
    if not camera:
        return 'Camera not found', 404
    return Response(_stream_generator(camera['url']), mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/api/scans', methods=['POST'])
def submit_scan():
    """Receive a barcode scan from a client."""
    data = request.get_json(silent=True) or {}
    code = data.get('code')
    if not code:
        return jsonify({'error': 'missing code'}), 400
    barcode_service.save_scan(code)
    return ('', 204)
