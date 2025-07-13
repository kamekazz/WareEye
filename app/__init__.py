from flask import Flask
from .services import camera_service


def create_app() -> Flask:
    camera_service.init_db()
    app = Flask(__name__)

    from .routes import detector, cameras

    app.register_blueprint(detector.bp)
    app.register_blueprint(cameras.bp)

    return app
