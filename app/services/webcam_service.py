import cv2
import threading
import queue
from pyzbar.pyzbar import decode, ZBarSymbol
from typing import Optional, Tuple

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


def _find_qr_region(gray: cv2.Mat) -> Optional[Tuple[int, int, int, int]]:
    """Locate the largest square-like contour that could contain a QR code."""
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best_rect: Optional[Tuple[int, int, int, int]] = None
    best_area = 0
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) != 4 or not cv2.isContourConvex(approx):
            continue
        x, y, w, h = cv2.boundingRect(approx)
        if h == 0:
            continue
        ratio = w / float(h)
        if ratio < 0.8 or ratio > 1.2:
            continue
        area = w * h
        if area > best_area:
            best_area = area
            best_rect = (x, y, w, h)
    return best_rect


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
        # Boost contrast to make barcode lines more distinct. CLAHE works well
        # under varying lighting conditions.
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        roi = _find_qr_region(enhanced)
        cropped = enhanced
        if roi is not None:
            x, y, w, h = roi
            cropped = enhanced[y : y + h, x : x + w]
        for code in decode(cropped, symbols=[ZBarSymbol.QRCODE]):
            try:
                text = code.data.decode("utf-8")
            except Exception:
                continue
            barcode_service.save_scan(text)
        yield jpg
