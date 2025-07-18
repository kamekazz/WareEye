import argparse
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Barcode scanning client")
    parser.add_argument("--camera-url", required=True, help="RTSP URL of the camera")
    parser.add_argument("--server", default="http://localhost:5000", help="WareEye server base URL")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.camera_url)
    if not cap.isOpened():
        print("Failed to open camera stream")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            for code in decode(gray, symbols=[ZBarSymbol.QRCODE]):
                try:
                    text = code.data.decode("utf-8")
                except Exception:
                    continue
                try:
                    requests.post(f"{args.server}/api/scans", json={"code": text}, timeout=1)
                except Exception as e:
                    print(f"Failed to send scan: {e}")
    finally:
        cap.release()


if __name__ == "__main__":
    main()
