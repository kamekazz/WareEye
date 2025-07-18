
import cv2
from pyzbar import pyzbar


def main() -> None:
    """Start the webcam stream and scan for barcodes or QR codes."""
    camera_url = 0
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print(f"Cannot open camera {camera_url}")
        return

    # Try to capture at a higher resolution to help with far away codes
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2000)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2000)

    detector = cv2.QRCodeDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        display_frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        data, bbox, _ = detector.detectAndDecode(gray)
        if bbox is not None and len(bbox):
            points = bbox.astype(int).reshape(-1, 2)
            cv2.polylines(display_frame, [points], isClosed=True, color=(0, 255, 0), thickness=2)
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
        else:
            barcodes = pyzbar.decode(gray)
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

        cv2.imshow("Security Camera Stream", display_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
