
import cv2


def main() -> None:
    """Start the webcam stream and scan for QR codes."""
    camera_url = 0
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print(f"Cannot open camera {camera_url}")
        return

    detector = cv2.QRCodeDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        data, bbox, _ = detector.detectAndDecode(frame)
        if bbox is not None and len(bbox):
            # bbox is returned as [[x1, y1], [x2, y2], ...]
            points = bbox.astype(int).reshape(-1, 2)
            color = (0, 255, 0) if data else (0, 0, 255)
            cv2.polylines(frame, [points], isClosed=True, color=color, thickness=2)
            if data:
                cv2.putText(
                    frame,
                    data,
                    tuple(points[0]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )

        cv2.imshow("Security Camera Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
