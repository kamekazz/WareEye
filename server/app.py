"""Application entrypoint for WareEye."""

from flask import Flask

from app.services import camera_service, barcode_service
from app.routes import cameras


# Initialize storage backends on startup
camera_service.init_db()
barcode_service.init_db()


app = Flask(__name__)
app.register_blueprint(cameras.bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
