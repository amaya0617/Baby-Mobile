# src/eye_worker.py

import cv2
import mediapipe as mp
import numpy as np
import threading
import time
from picamera2 import Picamera2


# =====================================================
# SHARED STATE
# =====================================================

class EyeState:
    def __init__(self, value="OPEN"):
        self.value = value


eye_state = EyeState("OPEN")
eye_lock = threading.Lock()


def get_eye_state() -> str:
    with eye_lock:
        return eye_state.value


# =====================================================
# EAR CALCULATION
# =====================================================

def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    if C == 0:
        return 0.0
    return (A + B) / (2.0 * C)


# =====================================================
# MEDIAPIPE SETUP
# =====================================================

mp_face_mesh = mp.solutions.face_mesh

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

EAR_THRESHOLD = 0.27
CLOSED_FRAMES = 5
OPEN_FRAMES = 5


# =====================================================
# EYE WORKER (PICAMERA2)
# =====================================================

def eye_worker(debug=False):
    print("🎥 Starting Picamera2 for eye detection...")

    picam = Picamera2()
    config = picam.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
    picam.configure(config)
    picam.start()

    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    closed_count = 0
    open_count = 0
    current_state = "OPEN"

    with eye_lock:
        eye_state.value = current_state

    print("👁 Eye worker running (Picamera2)")

    while True:
        frame = picam.capture_array()

        if frame is None:
            time.sleep(0.05)
            continue

        rgb = frame  # already RGB888

        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            face = results.multi_face_landmarks[0]
            h, w, _ = rgb.shape

            left_eye = np.array(
                [[face.landmark[i].x * w, face.landmark[i].y * h]
                 for i in LEFT_EYE],
                dtype=np.float32
            )

            right_eye = np.array(
                [[face.landmark[i].x * w, face.landmark[i].y * h]
                 for i in RIGHT_EYE],
                dtype=np.float32
            )

            ear = (
                eye_aspect_ratio(left_eye) +
                eye_aspect_ratio(right_eye)
            ) / 2.0

            if ear < EAR_THRESHOLD:
                closed_count += 1
                open_count = 0
            else:
                open_count += 1
                closed_count = 0

            prev = current_state

            if current_state == "OPEN" and closed_count >= CLOSED_FRAMES:
                current_state = "CLOSED"
                closed_count = open_count = 0

            elif current_state == "CLOSED" and open_count >= OPEN_FRAMES:
                current_state = "OPEN"
                closed_count = open_count = 0

            with eye_lock:
                eye_state.value = current_state

            if current_state != prev:
                print(f"👁 Eye state → {current_state}")

            if debug:
                print(f"EAR={ear:.3f} | STATE={current_state}")

        time.sleep(0.03)
