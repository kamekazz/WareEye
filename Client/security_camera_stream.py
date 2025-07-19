
import os
import argparse
import urllib.request
import time
from typing import Dict

import cv2
import requests
from pyzbar import pyzbar
try:
    from ultralytics import YOLO
except ImportError:  # pragma: no cover - optional dependency
    YOLO = None  # type: ignore


def ensure_wechat_models(det_proto: str, det_model: str, sr_proto: str, sr_model: str) -> None:
    """Download WeChatQRCode models if they don't exist."""
    base_url = "https://raw.githubusercontent.com/WeChatCV/opencv_3rdparty/wechat_qrcode/"
    for path in [det_proto, det_model, sr_proto, sr_model]:
        if not os.path.exists(path):
            url = base_url + os.path.basename(path)
            try:
                print(f"Downloading {url} ...")
                urllib.request.urlretrieve(url, path)
            except Exception as exc:  # pragma: no cover - network issues
                print(f"Failed to download {url}: {exc}")


def parse_camera_info(info_path: str) -> Dict[str, str]:
    """Parse camera metadata from the info file."""
    info: Dict[str, str] = {}
    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                    info[key.strip()] = value.strip()
    return info


def send_barcode(data: str, info: Dict[str, str], last: Dict[str, str]) -> None:
    """Send scanned barcode data to the server."""
    if not data:
        return

    now = time.time()

    # Skip sending if this barcode was already sent or if we recently sent
    if data == last.get("barcode"):
        return

    if now - last.get("time", 0) < 1:
        return

    payload = {
        "barcode": data,
        "camera_name": info.get("Camera Name", ""),
        "camera_area": info.get("Camera Area", ""),
        "camera_type": info.get("Camera Type", ""),
    }
    url = f"http://{info.get('Server IP', 'localhost')}:{info.get('Port', '5000')}/scan"

    try:
        requests.post(url, json=payload, timeout=2)
    except Exception as exc:  # pragma: no cover - network or server errors
        print(f"Failed to send barcode data: {exc}")

    last["barcode"] = data
    last["time"] = now


def main() -> None:
    """Start the webcam stream and scan for barcodes or QR codes."""
    parser = argparse.ArgumentParser(
        description="Start the webcam stream and scan for barcodes or QR codes."
    )
    parser.add_argument(
        "--model-path",
        default=os.getenv("YOLO_MODEL_PATH", "barcode_yolo.pt"),
        help="Path to the YOLO model for barcode detection",
    )
    parser.add_argument(
        "--wechat-det-prototxt",
        default=os.getenv("WECHAT_DET_PROTOTXT", "detect.prototxt"),
        help="Path to WeChat QRCode detection prototxt file",
    )
    parser.add_argument(
        "--wechat-det-model",
        default=os.getenv("WECHAT_DET_MODEL", "detect.caffemodel"),
        help="Path to WeChat QRCode detection model file",
    )
    parser.add_argument(
        "--wechat-sr-prototxt",
        default=os.getenv("WECHAT_SR_PROTOTXT", "sr.prototxt"),
        help="Path to WeChat QRCode super resolution prototxt file",
    )
    parser.add_argument(
        "--wechat-sr-model",
        default=os.getenv("WECHAT_SR_MODEL", "sr.caffemodel"),
        help="Path to WeChat QRCode super resolution model file",
    )

    args = parser.parse_args()

    # Load previous camera metadata if available and prompt for updates
    info_path = os.path.join(os.path.dirname(__file__), "camera_info.txt")
    prev_info = parse_camera_info(info_path)

    camera_name = input(
        f"Camera Name [{prev_info.get('Camera Name', '')}]: "
    ) or prev_info.get("Camera Name", "")
    camera_area = input(
        f"Camera Area [{prev_info.get('Camera Area', '')}]: "
    ) or prev_info.get("Camera Area", "")
    camera_type = input(
        f"Camera Type [{prev_info.get('Camera Type', '')}]: "
    ) or prev_info.get("Camera Type", "")
    server_IP = input(
        f"Server IP [{prev_info.get('Server IP', '')}]: "
    ) or prev_info.get("Server IP", "")
    port = input(f"Port [{prev_info.get('Port', '')}]: ") or prev_info.get("Port", "")

    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"Camera Name: {camera_name}\n")
        f.write(f"Camera Area: {camera_area}\n")
        f.write(f"Camera Type: {camera_type}\n")
        f.write(f"Server IP: {server_IP}\n")
        f.write(f"Port: {port}\n")

    print(f"Camera info saved to {info_path}")

    camera_info = parse_camera_info(info_path)
    last_scanned: Dict[str, str] = {}

    ensure_wechat_models(
        args.wechat_det_prototxt,
        args.wechat_det_model,
        args.wechat_sr_prototxt,
        args.wechat_sr_model,
    )
    CAMERA_PASS = 'titalovA'
    CAMERA_IP = '192.168.1.163'
    # camera_url = f"rtsp://admin:{CAMERA_PASS}@{CAMERA_IP}:554/h264Preview_01_main"
    camera_url = 0
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print(f"Cannot open camera {camera_url}")
        return

    # Try to capture at a higher resolution to help with far away codes
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    detector = cv2.QRCodeDetector()
    barcode_detector = cv2.barcode_BarcodeDetector() # type: ignore

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

    # Load YOLO model for barcode detection if available
    yolo_model = None
    if YOLO is not None:
        model_path = args.model_path
        if os.path.exists(model_path):
            try:
                yolo_model = YOLO(model_path)
            except Exception as exc:  # pragma: no cover - model loading is optional
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
                        for bbox in results.boxes.xyxy.tolist(): # type: ignore
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


if __name__ == '__main__':
    main()
