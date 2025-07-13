from flask import Flask
from .services import camera_service


def create_app() -> Flask:
    camera_service.init_db()

    app = Flask(__name__, template_folder="../templates")

    from .routes import webcam, cameras

    app.register_blueprint(webcam.bp)
    app.register_blueprint(cameras.bp)

    return app
