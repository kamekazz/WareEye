from datetime import datetime
from flask import Blueprint, jsonify, render_template, request

from models import db, Scan, DockDoor, OLPNLabel

bp = Blueprint("scan", __name__)


@bp.route("/")
def hello():
    return render_template("home.html")


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
            camera_name=data["camera_name"],  # type: ignore
            area=data["area"],  # type: ignore
            camera_type=data["camera_type"],  # type: ignore
            client_ip=data["client_ip"],  # type: ignore
            camera_url=data["camera_url"],  # type: ignore
            barcode=data["barcode"],  # type: ignore
            timestamp=timestamp,  # type: ignore
        )
    except Exception as exc:  # pragma: no cover - input errors
        return jsonify({"error": f"Invalid payload: {exc}"}), 400

    db.session.add(scan)

    valid = None
    if scan.area.startswith("DD"):
        dock = DockDoor.query.filter_by(name=scan.area).first()
        label = OLPNLabel.query.filter_by(barcode=scan.barcode).first()
        valid = (
            dock is not None
            and label is not None
            and label.destination_code_id == dock.destination_code_id
        )
        if valid and label.status != "shipped":  # type: ignore[union-attr]
            label.status = "shipped"  # type: ignore[union-attr]
            label.updated_at = datetime.utcnow()  # type: ignore[union-attr]
            db.session.add(label)  # ensure updated

    db.session.commit()

    resp = {"status": "success", "id": scan.id}
    if valid is not None:
        resp["valid"] = valid
    return jsonify(resp)  # type: ignore


