"""Simple Flask application for barcode scan ingestion and CRUD UI."""

from datetime import datetime

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    flash,
    Blueprint,
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev"
db = SQLAlchemy(app)
CORS(app)

class Scan(db.Model):
    """Database model for a scan event."""

    id = db.Column(db.Integer, primary_key=True)
    camera_name = db.Column(db.String, nullable=False)
    area = db.Column(db.String, nullable=False)
    camera_type = db.Column(db.String, nullable=False)
    client_ip = db.Column(db.String, nullable=False)
    camera_url = db.Column(db.String, nullable=False)
    barcode = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover - representation only
        return f"<Scan {self.id} {self.barcode}>"

@app.route('/')
def hello():
    return 'Hello, World from Flask!'


bp = Blueprint("scan", __name__)


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
    """Render a table with all scans."""
    scans = Scan.query.order_by(Scan.timestamp.desc()).all()
    return render_template("scans.html", scans=scans)


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


app.register_blueprint(bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
