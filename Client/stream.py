# -*- coding: utf-8 -*-
"""Camera streaming and barcode detection loop."""

from __future__ import annotations

import os
from typing import Dict

import cv2
from pyzbar import pyzbar

from utils import send_barcode

try:
    from ultralytics import YOLO
except ImportError:  # pragma: no cover - optional dependency
    YOLO = None  # type: ignore


def run_stream(cap: cv2.VideoCapture, camera_info: Dict[str, str], args) -> None:
    """Display ``cap`` frames and detect barcodes/QR codes."""
    last_scanned: Dict[str, float] = {}

    detector = cv2.QRCodeDetector()
    barcode_detector = cv2.barcode_BarcodeDetector()  # type: ignore

    wechat_detector = None
    if hasattr(cv2, "wechat_qrcode"):
        try:
            wechat_detector = cv2.wechat_qrcode.WeChatQRCode(
                args.wechat_det_prototxt,
                args.wechat_det_model,
                args.wechat_sr_prototxt,
                args.wechat_sr_model,
            )
        except Exception as exc:  # pragma: no cover - optional dependency
            print(f"Failed to load WeChatQRCode models: {exc}")

    yolo_model = None
    if YOLO is not None:
        model_path = args.model_path
        if os.path.exists(model_path):
            try:
                yolo_model = YOLO(model_path)
            except Exception as exc:  # pragma: no cover - model loading optional
                print(f"Failed to load YOLO model from {model_path}: {exc}")
        else:
            print(
                f"YOLO model file '{model_path}' not found. Barcode detection with YOLO disabled."
            )

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        frame = cv2.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        display_frame = frame.copy()

        retval, decoded_info, points, _ = barcode_detector.detectAndDecodeMulti(gray)
        if retval:
            for text, pts in zip(decoded_info, points):
                if text:
                    pts = pts.astype(int).reshape(-1, 2)
                    cv2.polylines(display_frame, [pts], True, (0, 255, 0), 2)
                    cv2.putText(
                        display_frame,
                        text,
                        tuple(pts[0]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2,
                    )
                    send_barcode(text, camera_info, last_scanned)
        else:
            data, bbox, _ = detector.detectAndDecode(gray)
            if bbox is not None and len(bbox):
                points = bbox.astype(int).reshape(-1, 2)
                cv2.polylines(display_frame, [points], True, (0, 255, 0), 2)
                if data:
                    cv2.putText(
                        display_frame,
                        data,
                        tuple(points[0]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2,
                    )
                    send_barcode(data, camera_info, last_scanned)
            else:
                texts, w_points = [], []
                if wechat_detector is not None:
                    try:
                        texts, w_points = wechat_detector.detectAndDecode(gray)
                    except Exception as exc:  # pragma: no cover - runtime issues
                        print(f"WeChatQRCode detection failed: {exc}")

                if w_points:
                    for text, pts in zip(texts, w_points):
                        pts = pts.astype(int).reshape(-1, 2)
                        cv2.polylines(display_frame, [pts], True, (0, 255, 0), 2)
                        if text:
                            cv2.putText(
                                display_frame,
                                text,
                                tuple(pts[0]),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (0, 255, 0),
                                2,
                            )
                            send_barcode(text, camera_info, last_scanned)
                else:
                    barcodes = pyzbar.decode(gray)
                    if not barcodes and yolo_model is not None:
                        results = yolo_model(frame, verbose=False)
                        for bbox in results.boxes.xyxy.tolist():  # type: ignore
                            x1, y1, x2, y2 = map(int, bbox)
                            roi = gray[y1:y2, x1:x2]
                            detected = pyzbar.decode(roi)
                            if detected:
                                for bc in detected:
                                    x, y, w, h = bc.rect
                                    cv2.rectangle(
                                        display_frame,
                                        (x1 + x, y1 + y),
                                        (x1 + x + w, y1 + y + h),
                                        (0, 255, 0),
                                        2,
                                    )
                                    barcode_data = bc.data.decode("utf-8")
                                    cv2.putText(
                                        display_frame,
                                        barcode_data,
                                        (x1 + x, y1 + y - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.6,
                                        (0, 255, 0),
                                        2,
                                    )
                                    send_barcode(barcode_data, camera_info, last_scanned)
                            else:
                                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    else:
                        for barcode in barcodes:
                            x, y, w, h = barcode.rect
                            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            barcode_data = barcode.data.decode("utf-8")
                            cv2.putText(
                                display_frame,
                                barcode_data,
                                (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (0, 255, 0),
                                2,
                            )
                            send_barcode(barcode_data, camera_info, last_scanned)

        cv2.imshow("Security Camera Stream", display_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
