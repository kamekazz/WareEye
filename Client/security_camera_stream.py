import cv2


def main():
    camera_url = 0
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print(f"Cannot open camera {camera_url}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break
        cv2.imshow('Security Camera Stream', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
