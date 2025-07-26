from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Scan(db.Model):
    """Database model for a scan event."""

    id = db.Column(db.Integer, primary_key=True)
    camera_name = db.Column(db.String, nullable=False, index=True)
    area = db.Column(db.String, nullable=False, index=True)
    camera_type = db.Column(db.String, nullable=False)
    client_ip = db.Column(db.String, nullable=False)
    camera_url = db.Column(db.String, nullable=False)
    barcode = db.Column(db.String, nullable=False, index=True)
    timestamp = db.Column(
        db.DateTime, nullable=False, index=True, default=datetime.utcnow
    )

    def __repr__(self) -> str:  # pragma: no cover - representation only
        return f"<Scan {self.id} {self.barcode}>"


class DestinationCode(db.Model):
    """Mapping of 3-letter codes to carrier names."""

    __tablename__ = "destination_codes"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - representation only
        return f"<DestinationCode {self.id} {self.code}>"


class DockDoor(db.Model):
    """Loading dock door linked to a destination code."""

    __tablename__ = "dock_doors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    destination_code_id = db.Column(
        db.Integer, db.ForeignKey("destination_codes.id"), nullable=False
    )
    description = db.Column(db.String, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    destination_code = db.relationship("DestinationCode")

    def __repr__(self) -> str:  # pragma: no cover - representation only
        return f"<DockDoor {self.id} {self.name}>"


class OLPNLabel(db.Model):
    """Label representing an outbound license plate number (OLPN)."""

    __tablename__ = "olpn_labels"

    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String, nullable=False, unique=True, index=True)
    destination_code_id = db.Column(
        db.Integer, db.ForeignKey("destination_codes.id"), nullable=False
    )
    status = db.Column(db.String(16), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    destination = db.relationship("DestinationCode")

    def __repr__(self) -> str:  # pragma: no cover - representation only
        return f"<OLPNLabel {self.id} {self.barcode}>"
