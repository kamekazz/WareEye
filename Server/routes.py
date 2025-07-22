from datetime import datetime
from flask import (
    Blueprint,
    jsonify,
    render_template,
    redirect,
    request,
    url_for,
    flash,
)

from models import db, Scan, DestinationCode, DockDoor

bp = Blueprint("scan", __name__)


@bp.route("/")
def hello():
    return "Hello, World from Flask!"


@bp.route("/api/scan", methods=["POST"])
def ingest_scan() -> tuple:
    """Ingest scan data from cameras."""
    data = request.get_json(force=True, silent=True) or {}
    try:
        timestamp = data.get("timestamp")
        if timestamp:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        else:
            timestamp = datetime.utcnow()
        scan = Scan(
            camera_name=data["camera_name"], # type: ignore
            area=data["area"], # type: ignore
            camera_type=data["camera_type"], # type: ignore
            client_ip=data["client_ip"], # type: ignore
            camera_url=data["camera_url"], # type: ignore
            barcode=data["barcode"], # type: ignore
            timestamp=timestamp, # type: ignore
        )
    except Exception as exc:  # pragma: no cover - input errors
        return jsonify({"error": f"Invalid payload: {exc}"}), 400

    db.session.add(scan)
    db.session.commit()
    return jsonify({"status": "success", "id": scan.id}) # type: ignore


@bp.route("/scans")
def list_scans() -> str:
    """Render a table of scans with optional filtering and pagination."""
    barcode = request.args.get("barcode")
    area = request.args.get("area")
    camera = request.args.get("camera_name")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    page = int(request.args.get("page", 1))

    q = Scan.query
    if barcode:
        q = q.filter(Scan.barcode.ilike(f"%{barcode}%"))
    if area:
        q = q.filter(Scan.area.ilike(f"%{area}%"))
    if camera:
        q = q.filter(Scan.camera_name.ilike(f"%{camera}%"))
    if start_date:
        q = q.filter(Scan.timestamp >= start_date)
    if end_date:
        q = q.filter(Scan.timestamp <= end_date)

    scans = (
        q.order_by(Scan.timestamp.desc()).paginate(page=page, per_page=50)
    )

    args = request.args.to_dict()
    args.pop("page", None)
    return render_template("scans.html", scans=scans, args=args)


@bp.route("/scans/<int:scan_id>/edit", methods=["GET", "POST"])
def edit_scan(scan_id: int):
    """Edit an existing scan record."""
    scan = Scan.query.get_or_404(scan_id)
    if request.method == "POST":
        try:
            scan.camera_name = request.form["camera_name"]
            scan.area = request.form["area"]
            scan.camera_type = request.form["camera_type"]
            scan.client_ip = request.form["client_ip"]
            scan.camera_url = request.form["camera_url"]
            scan.barcode = request.form["barcode"]
            scan.timestamp = datetime.fromisoformat(
                request.form["timestamp"].replace("Z", "+00:00")
            )
            db.session.commit()
            flash("Scan updated", "success")
            return redirect(url_for("scan.list_scans"))
        except Exception as exc:  # pragma: no cover - input errors
            flash(f"Failed to update scan: {exc}", "danger")
    return render_template("scan_edit.html", scan=scan)


@bp.route("/scans/<int:scan_id>/delete", methods=["POST"])
def delete_scan(scan_id: int):
    """Delete a scan record."""
    scan = Scan.query.get_or_404(scan_id)
    db.session.delete(scan)
    db.session.commit()
    flash("Scan deleted", "success")
    return redirect(url_for("scan.list_scans"))


@bp.route("/destination-codes", methods=["GET", "POST"])
def list_destination_codes() -> str:
    """Show all destination codes and handle creation."""
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        name = request.form.get("name", "").strip()
        if not code or not name:
            flash("Code and Name are required", "danger")
        elif DestinationCode.query.filter_by(code=code).first():
            flash("Code already exists", "danger")
        else:
            db.session.add(DestinationCode(code=code, name=name))
            db.session.commit()
            flash("Destination code added", "success")
            return redirect(url_for("scan.list_destination_codes"))
    codes = DestinationCode.query.order_by(DestinationCode.code).all()
    return render_template("destination_codes.html", codes=codes)


@bp.route("/destination-codes/<int:code_id>/edit", methods=["GET", "POST"])
def edit_destination_code(code_id: int):
    """Edit a destination code."""
    code_obj = DestinationCode.query.get_or_404(code_id)
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        name = request.form.get("name", "").strip()
        if not code or not name:
            flash("Code and Name are required", "danger")
        elif DestinationCode.query.filter(
            DestinationCode.code == code, DestinationCode.id != code_id
        ).first():
            flash("Code already exists", "danger")
        else:
            code_obj.code = code
            code_obj.name = name
            db.session.commit()
            flash("Destination code updated", "success")
            return redirect(url_for("scan.list_destination_codes"))
    return render_template("destination_code_edit.html", code=code_obj)


@bp.route("/destination-codes/<int:code_id>/delete", methods=["POST"])
def delete_destination_code(code_id: int):
    """Delete a destination code."""
    code_obj = DestinationCode.query.get_or_404(code_id)
    db.session.delete(code_obj)
    db.session.commit()
    flash("Destination code deleted", "success")
    return redirect(url_for("scan.list_destination_codes"))


@bp.route("/dock-doors", methods=["GET", "POST"])
def list_dock_doors() -> str:
    """List dock doors and handle creation."""
    codes = DestinationCode.query.order_by(DestinationCode.code).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        destination_id = request.form.get("destination_code_id")
        if not name or not destination_id:
            flash("Name and Destination are required", "danger")
        elif DockDoor.query.filter_by(name=name).first():
            flash("Name already exists", "danger")
        else:
            dock = DockDoor(name=name, destination_code_id=int(destination_id))
            db.session.add(dock)
            db.session.commit()
            flash("Dock door added", "success")
            return redirect(url_for("scan.list_dock_doors"))

    doors = DockDoor.query.order_by(DockDoor.created_at.desc()).all()
    return render_template("dock_doors.html", doors=doors, codes=codes)


@bp.route("/dock-doors/<int:door_id>/edit", methods=["GET", "POST"])
def edit_dock_door(door_id: int):
    """Edit a dock door."""
    door = DockDoor.query.get_or_404(door_id)
    codes = DestinationCode.query.order_by(DestinationCode.code).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        destination_id = request.form.get("destination_code_id")
        if not name or not destination_id:
            flash("Name and Destination are required", "danger")
        elif DockDoor.query.filter(DockDoor.name == name, DockDoor.id != door_id).first():
            flash("Name already exists", "danger")
        else:
            door.name = name
            door.destination_code_id = int(destination_id)
            door.is_active = bool(request.form.get("is_active"))
            door.description = request.form.get("description") or None
            db.session.commit()
            flash("Dock door updated", "success")
            return redirect(url_for("scan.list_dock_doors"))
    return render_template("dock_door_edit.html", door=door, codes=codes)


@bp.route("/dock-doors/<int:door_id>/delete", methods=["POST"])
def delete_dock_door(door_id: int):
    """Delete a dock door."""
    door = DockDoor.query.get_or_404(door_id)
    db.session.delete(door)
    db.session.commit()
    flash("Dock door deleted", "success")
    return redirect(url_for("scan.list_dock_doors"))
