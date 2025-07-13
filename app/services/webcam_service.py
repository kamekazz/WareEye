import cv2
import threading
import queue
from pyzbar.pyzbar import decode, ZBarSymbol

from . import barcode_service

_cap = cv2.VideoCapture(0)

# Attempt to lock camera settings for consistent exposure/white balance/focus.
try:
    _cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
    _cap.set(cv2.CAP_PROP_AUTO_WB, 0)
     # Enable autofocus to ensure the image stays sharp.
    _cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
except Exception:
    pass

_lock = threading.Lock()
_frame_queue: "queue.Queue[cv2.Mat]" = queue.Queue(maxsize=1)
_stop_event = threading.Event()


def _capture_loop() -> None:
    """Continuously capture frames in a separate thread."""
    while not _stop_event.is_set():
        with _lock:
            ret, frame = _cap.read()
        if not ret:
            continue
        # Keep only the most recent frame to avoid lag.
        if _frame_queue.full():
            try:
                _frame_queue.get_nowait()
            except queue.Empty:
                pass
        _frame_queue.put(frame)


_thread = threading.Thread(target=_capture_loop, daemon=True)
_thread.start()


def get_frame():
    """Retrieve the latest frame from the capture thread."""
    try:
        frame = _frame_queue.get(timeout=0.1)
    except queue.Empty:
        return None, None
    ret, buf = cv2.imencode('.jpg', frame)
    jpg = buf.tobytes() if ret else None
    return frame, jpg


def frames():
    """Generator yielding JPEG-encoded frames with barcode decoding."""
    while True:
        frame, jpg = get_frame()
        if jpg is None:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for code in decode(gray, symbols=[ZBarSymbol.QRCODE]):
            try:
                text = code.data.decode("utf-8")
            except Exception:
                continue
            barcode_service.save_scan(text)
        yield jpg
