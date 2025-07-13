from app import create_app
from app.services.detector_service import start as start_detection

app = create_app()

if __name__ == '__main__':
    start_detection()
    app.run(host='0.0.0.0', port=5000)
