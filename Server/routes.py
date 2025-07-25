from datetime import datetime
from flask import Blueprint, jsonify, render_template, request

from models import db, Scan

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
    db.session.commit()
    return jsonify({"status": "success", "id": scan.id})  # type: ignore


