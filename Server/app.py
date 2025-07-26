"""Simple Flask application for barcode scan ingestion and CRUD UI."""

from flask import Flask
from flask_cors import CORS
from models import db  # type: ignore
from routes import bp
from facility_routes import facility_bp
from operations_routes import operations_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev"# This should be changed in production
db.init_app(app)
CORS(app)

app.register_blueprint(bp)
app.register_blueprint(facility_bp)
app.register_blueprint(operations_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
