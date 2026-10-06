from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()

picam2.configure(
    picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
)

picam2.start()
print("✅ Camera started — press Q to exit")

while True:
    frame = picam2.capture_array()

    if frame is None:
        print("❌ No frame received")
        time.sleep(0.1)
        continue

    cv2.imshow("Pi Camera Live Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

picam2.stop()
cv2.destroyAllWindows()
