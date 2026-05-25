from picamera2 import Picamera2
import cv2
import numpy as np

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

prev_frame = None

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if prev_frame is None:
        prev_frame = gray
        continue

    diff = cv2.absdiff(prev_frame, gray)
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]

    motion_score = np.sum(thresh)

    if motion_score > 2_000_000:
        cv2.putText(frame, "MOTION DETECTED", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        print("MOTION!")
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)

            cx = x + w // 2
            cy = y + h // 2

            print("Target Coords:", cx, cy)

    # cv2.imshow("Turret Cam", frame)
    prev_frame = gray

    if cv2.waitKey(1) == 27:  # ESC to exit
        break

cv2.destroyAllWindows()