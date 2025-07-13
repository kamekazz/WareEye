import cv2
import threading
from pyzbar import pyzbar

from . import barcode_service

_cap = cv2.VideoCapture(0)
_lock = threading.Lock()


def get_frame():
    with _lock:
        if not _cap.isOpened():
            return None, None
        ret, frame = _cap.read()
    if not ret:
        return None, None
    ret, buf = cv2.imencode('.jpg', frame)
    jpg = buf.tobytes() if ret else None
    return frame, jpg


def frames():
    while True:
        frame, jpg = get_frame()
        if jpg is None:
            continue
        for code in pyzbar.decode(frame):
            try:
                text = code.data.decode("utf-8")
            except Exception:
                continue
            barcode_service.save_scan(text)
        yield jpg
