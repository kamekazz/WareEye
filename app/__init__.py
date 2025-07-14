from flask import Flask
from .services import camera_service, barcode_service


def create_app() -> Flask:
    camera_service.init_db()
    barcode_service.init_db()

    app = Flask(__name__, template_folder="../templates")

    from .routes import cameras

    app.register_blueprint(cameras.bp)

    return app
