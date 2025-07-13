import cv2
import threading

_cap = cv2.VideoCapture(0)
_lock = threading.Lock()


def get_frame():
    with _lock:
        if not _cap.isOpened():
            return None
        ret, frame = _cap.read()
        if not ret:
            return None
        ret, buf = cv2.imencode('.jpg', frame)
        return buf.tobytes() if ret else None


def frames():
    while True:
        frame = get_frame()
        if frame is None:
            continue
        yield frame
