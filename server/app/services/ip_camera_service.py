import cv2
from typing import Generator


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


