import cv2
import time
import threading
import sqlite3
from datetime import datetime
from pyzbar import pyzbar
import os

class BarcodeDetector(threading.Thread):
    """Threaded barcode detection and tracking."""

    def __init__(self, stream_url, db_path="pallets.db"):
        super().__init__(daemon=True)
        self.stream_url = stream_url
        self.db_path = db_path
        self.cap = None
        self.running = threading.Event()
        self.frame_lock = threading.Lock()
        self.current_frame = None
        self.trackers = {}
        self.next_id = 1
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS pallets (id INTEGER, barcode TEXT, timestamp TEXT, x REAL, y REAL)"
        )
        conn.commit()
        conn.close()

    def connect(self):
        """(Re)connect to the camera stream using FFMPEG with TCP transport."""
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.stream_url, cv2.CAP_FFMPEG)

    def run(self):
        self.running.set()
        failures = 0
        while self.running.is_set():
            if self.cap is None or not self.cap.isOpened():
                self.connect()
                failures += 1
                time.sleep(min(5, 2 ** failures))
                continue
            ret, frame = self.cap.read()
            if not ret:
                self.connect()
                failures += 1
                time.sleep(min(5, 2 ** failures))
                continue
            failures = 0
            processed = self.process_frame(frame)
            with self.frame_lock:
                self.current_frame = processed

    def stop(self):
        self.running.clear()
        if self.cap:
            self.cap.release()

    def process_frame(self, frame):
        detections = pyzbar.decode(frame)
        for d in detections:
            x, y, w, h = d.rect
            cx, cy = x + w / 2, y + h / 2
            barcode = d.data.decode("utf-8")
            if barcode in self.trackers:
                tid = self.trackers[barcode]["id"]
            else:
                tid = self.next_id
                self.trackers[barcode] = {"id": tid}
                self.next_id += 1
            self.trackers[barcode].update({"centroid": (cx, cy), "last_seen": time.time()})
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"ID:{tid}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            self._log_detection(tid, barcode, cx, cy)
        return frame

    def _log_detection(self, tid, barcode, cx, cy):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO pallets (id, barcode, timestamp, x, y) VALUES (?, ?, ?, ?, ?)",
            (tid, barcode, datetime.utcnow().isoformat(), cx, cy),
        )
        conn.commit()
        conn.close()

    def get_frame(self):
        with self.frame_lock:
            if self.current_frame is None:
                return None
            ret, buf = cv2.imencode(".jpg", self.current_frame)
            return buf.tobytes() if ret else None
