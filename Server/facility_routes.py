from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    url_for,
    flash,
    jsonify,
    send_file,
)

from models import db, Scan, DestinationCode, DockDoor, OLPNLabel

facility_bp = Blueprint("facility", __name__, url_prefix="/facility")


@facility_bp.route("/scans")
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

    scans = q.order_by(Scan.timestamp.desc()).paginate(page=page, per_page=50)

    args = request.args.to_dict()
    args.pop("page", None)
    return render_template("facility/scans.html", scans=scans, args=args)


@facility_bp.route("/scans/<int:scan_id>/edit", methods=["GET", "POST"])
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
            return redirect(url_for("facility.list_scans"))
        except Exception as exc:  # pragma: no cover - input errors
            flash(f"Failed to update scan: {exc}", "danger")
    return render_template("facility/scan_edit.html", scan=scan)


@facility_bp.route("/scans/<int:scan_id>/delete", methods=["POST"])
def delete_scan(scan_id: int):
    """Delete a scan record."""
    scan = Scan.query.get_or_404(scan_id)
    db.session.delete(scan)
    db.session.commit()
    flash("Scan deleted", "success")
    return redirect(url_for("facility.list_scans"))


@facility_bp.route("/destination-codes", methods=["GET", "POST"])
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
            db.session.add(DestinationCode(code=code, name=name))  # type: ignore
            db.session.commit()
            flash("Destination code added", "success")
            return redirect(url_for("facility.list_destination_codes"))
    codes = DestinationCode.query.order_by(DestinationCode.code).all()
    return render_template("facility/destination_codes.html", codes=codes)


@facility_bp.route("/destination-codes/<int:code_id>/edit", methods=["GET", "POST"])
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
            return redirect(url_for("facility.list_destination_codes"))
    return render_template("facility/destination_code_edit.html", code=code_obj)


@facility_bp.route("/destination-codes/<int:code_id>/delete", methods=["POST"])
def delete_destination_code(code_id: int):
    """Delete a destination code."""
    code_obj = DestinationCode.query.get_or_404(code_id)
    db.session.delete(code_obj)
    db.session.commit()
    flash("Destination code deleted", "success")
    return redirect(url_for("facility.list_destination_codes"))


@facility_bp.route("/dock-doors", methods=["GET", "POST"])
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
            return redirect(url_for("facility.list_dock_doors"))

    doors = DockDoor.query.order_by(DockDoor.created_at.desc()).all()
    return render_template("facility/dock_doors.html", doors=doors, codes=codes)


@facility_bp.route("/dock-doors/<int:door_id>/edit", methods=["GET", "POST"])
def edit_dock_door(door_id: int):
    """Edit a dock door."""
    door = DockDoor.query.get_or_404(door_id)
    codes = DestinationCode.query.order_by(DestinationCode.code).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        destination_id = request.form.get("destination_code_id")
        if not name or not destination_id:
            flash("Name and Destination are required", "danger")
        elif DockDoor.query.filter(
            DockDoor.name == name, DockDoor.id != door_id
        ).first():
            flash("Name already exists", "danger")
        else:
            door.name = name
            door.destination_code_id = int(destination_id)
            door.is_active = bool(request.form.get("is_active"))
            door.description = request.form.get("description") or None
            db.session.commit()
            flash("Dock door updated", "success")
            return redirect(url_for("facility.list_dock_doors"))
    return render_template("facility/dock_door_edit.html", door=door, codes=codes)


@facility_bp.route("/dock-doors/<int:door_id>/delete", methods=["POST"])
def delete_dock_door(door_id: int):
    """Delete a dock door."""
    door = DockDoor.query.get_or_404(door_id)
    db.session.delete(door)
    db.session.commit()
    flash("Dock door deleted", "success")
    return redirect(url_for("facility.list_dock_doors"))


@facility_bp.route("/olpn-labels", methods=["GET", "POST"])
def list_olpn_labels() -> str:
    """List OLPN labels and handle creation."""
    codes = DestinationCode.query.order_by(DestinationCode.code).all()
    if request.method == "POST":
        barcode = request.form.get("barcode", "").strip()
        destination_id = request.form.get("destination_code_id")
        if not barcode or not destination_id:
            flash("Barcode and Destination are required", "danger")
        elif OLPNLabel.query.filter_by(barcode=barcode).first():
            flash("Barcode already exists", "danger")
        else:
            label = OLPNLabel(barcode=barcode, destination_code_id=int(destination_id))
            db.session.add(label)
            db.session.commit()
            flash("Label added", "success")
            return redirect(url_for("facility.list_olpn_labels"))
    labels = OLPNLabel.query.order_by(OLPNLabel.created_at.desc()).all()
    return render_template("facility/olpn_labels.html", labels=labels, codes=codes)


@facility_bp.route("/olpn-labels/<int:label_id>/pdf")
def olpn_label_pdf(label_id: int):
    """Generate a PDF with the label's QR code."""
    label = OLPNLabel.query.get_or_404(label_id)

    import io
    import qrcode
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    qr_img = qrcode.make(label.barcode)
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=landscape(letter))

    width, height = landscape(letter)
    half_width = width / 2
    margin = 36
    barcode_size = 200
    y_img = (height - barcode_size) / 2

    for offset in (margin, half_width + margin):
        c.drawImage(
            ImageReader(img_buffer),
            offset,
            y_img,
            width=barcode_size,
            height=barcode_size,
        )
        c.setFont("Helvetica", 14)
        text_y = y_img - 20
        c.drawCentredString(offset + barcode_size / 2, text_y, label.barcode)
        c.setFont("Helvetica", 12)
        c.drawCentredString(
            offset + barcode_size / 2,
            text_y - 18,
            f"Destination: {label.destination.code}",
        )
        c.setFont("Helvetica", 8)
        c.drawCentredString(
            offset + barcode_size / 2,
            margin,
            f'Created: {label.created_at.strftime("%Y-%m-%d %H:%M")}',
        )

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    filename = f"label_{label.barcode}.pdf"
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@facility_bp.route("/olpn-labels/<int:label_id>/edit", methods=["GET", "POST"])
def edit_olpn_label(label_id: int):
    """Edit an OLPN label."""
    label = OLPNLabel.query.get_or_404(label_id)
    codes = DestinationCode.query.order_by(DestinationCode.code).all()
    if request.method == "POST":
        barcode = request.form.get("barcode", "").strip()
        destination_id = request.form.get("destination_code_id")
        status = request.form.get("status")
        if not barcode or not destination_id or not status:
            flash("Barcode, Destination and Status are required", "danger")
        elif OLPNLabel.query.filter(
            OLPNLabel.barcode == barcode, OLPNLabel.id != label_id
        ).first():
            flash("Barcode already exists", "danger")
        else:
            label.barcode = barcode
            label.destination_code_id = int(destination_id)
            if status in ("pending", "shipped"):
                label.status = status
            db.session.commit()
            flash("Label updated", "success")
            return redirect(url_for("facility.list_olpn_labels"))
    return render_template("facility/olpn_label_edit.html", label=label, codes=codes)


@facility_bp.route("/olpn-labels/<int:label_id>/delete", methods=["POST"])
def delete_olpn_label(label_id: int):
    """Delete an OLPN label."""
    label = OLPNLabel.query.get_or_404(label_id)
    db.session.delete(label)
    db.session.commit()
    flash("Label deleted", "success")
    return redirect(url_for("facility.list_olpn_labels"))
