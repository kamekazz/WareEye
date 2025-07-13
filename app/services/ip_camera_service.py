import cv2
import threading
from typing import Generator, Dict
from pyzbar.pyzbar import decode, ZBarSymbol

from . import barcode_service

_scanner_threads: Dict[int, threading.Event] = {}


def frames(url: str) -> Generator[bytes, None, None]:
    """Yield JPEG-encoded frames from the given stream URL."""
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        return
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            ret, buf = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield buf.tobytes()
    finally:
        cap.release()


def _scan_loop(url: str, stop_event: threading.Event) -> None:
    """Continuously capture frames from the IP camera and decode QR codes."""
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        return
    try:
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            for code in decode(gray, symbols=[ZBarSymbol.QRCODE]):
                try:
                    text = code.data.decode("utf-8")
                except Exception:
                    continue
                barcode_service.save_scan(text)
    finally:
        cap.release()


def start_scanning(camera_id: int, url: str) -> None:
    """Start a background scanning thread for the given camera if not running."""
    if camera_id in _scanner_threads:
        return
    stop_event = threading.Event()
    thread = threading.Thread(target=_scan_loop, args=(url, stop_event), daemon=True)
    _scanner_threads[camera_id] = stop_event
    thread.start()


def stop_scanning(camera_id: int) -> None:
    """Stop the scanning thread for the given camera if it exists."""
    event = _scanner_threads.pop(camera_id, None)
    if event:
        event.set()
