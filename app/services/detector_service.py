import os
import time
from dotenv import load_dotenv

from .detector import BarcodeDetector

load_dotenv()

CAMERA_IP = os.getenv("CAMERA_IP", "192.168.1.163")
CAMERA_PASS = os.getenv("CAMERA_PASS", "")
# Additional options passed to OpenCV when opening the RTSP stream. By default
# TCP is used to reduce packet loss.
RTSP_OPTIONS = os.getenv("RTSP_OPTIONS", "rtsp_transport=tcp")

STREAM_URL = f"rtsp://admin:{CAMERA_PASS}@{CAMERA_IP}:554/h264Preview_01_main"
if RTSP_OPTIONS:
    STREAM_URL += f"?{RTSP_OPTIONS}"

# Shared detector instance used by the Flask routes

detector = BarcodeDetector(STREAM_URL)


def start() -> None:
    """Start the barcode detection thread if not already running."""
    if not detector.is_alive():
        detector.start()


def stop() -> None:
    """Stop the barcode detection thread."""
    detector.stop()


def frames():
    """Yield processed video frames for streaming to clients."""
    while True:
        frame = detector.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
        yield (
            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


def health() -> str:
    """Return the health status of the detection thread."""
    return "ok" if detector.is_alive() else "detector stopped"
