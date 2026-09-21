# src/main.py

import time
import threading
import numpy as np
import sounddevice as sd
import tflite_runtime.interpreter as tflite

from ring_buffer import RingBuffer
from audio_player import AudioPlayer
from eye_worker import eye_worker, get_eye_state
from servo_controller import ServoController
from light_controller import LightController


# ======================================================
# SHARED ML OUTPUT
# ======================================================
latest_chunk_label = "neutral"
label_lock = threading.Lock()


# ======================================================
# PARAMETERS
# ======================================================
SAMPLE_RATE = 16000
WINDOW_SEC = 1.0
BUFFER_SEC = 5.0

YAMNET_PATH = "models/yamnet.tflite"
CLASSIFIER_PATH = "models/classifier.tflite"

CLASS_NAMES = ["cry", "laugh", "noise", "silence"]

ENTER_THRESHOLD = 2
EXIT_THRESHOLD = 5
SWITCH_THRESHOLD = 5

CONFIDENCE_THRESHOLD = 0.6
ENERGY_THRESHOLD = 0.09


# ======================================================
# DEVICES
# ======================================================
audio_player = AudioPlayer()
servo = ServoController(pin=18)
light = LightController(pin=23)   # relay pin


# ======================================================
# RING BUFFER
# ======================================================
rb = RingBuffer(int(BUFFER_SEC * SAMPLE_RATE))


# ======================================================
# AUDIO CALLBACK
# ======================================================
def audio_callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status)

    rb.write(indata[:, 0])


# ======================================================
# LOAD TFLITE MODELS
# ======================================================
yamnet = tflite.Interpreter(model_path=YAMNET_PATH)
yamnet.allocate_tensors()

y_input = yamnet.get_input_details()
y_output = yamnet.get_output_details()

classifier = tflite.Interpreter(model_path=CLASSIFIER_PATH)
classifier.allocate_tensors()

c_input = classifier.get_input_details()
c_output = classifier.get_output_details()


# ======================================================
# ML WORKER THREAD
# ======================================================
def ml_worker():
    global latest_chunk_label

    print("🎧 ML worker started")

    while True:
        time.sleep(WINDOW_SEC)

        waveform = rb.read_latest(int(WINDOW_SEC * SAMPLE_RATE))

        if len(waveform) < int(WINDOW_SEC * SAMPLE_RATE):
            continue

        rms = np.sqrt(np.mean(waveform ** 2))

        if rms < ENERGY_THRESHOLD:
            with label_lock:
                latest_chunk_label = "neutral"
            continue

        yamnet.resize_tensor_input(
            y_input[0]["index"], [waveform.shape[0]]
        )
        yamnet.allocate_tensors()

        yamnet.set_tensor(y_input[0]["index"], waveform)
        yamnet.invoke()

        embeddings = yamnet.get_tensor(y_output[1]["index"])

        labels = []

        for emb in embeddings:
            emb = np.expand_dims(emb, axis=0).astype(np.float32)

            classifier.set_tensor(c_input[0]["index"], emb)
            classifier.invoke()

            probs = classifier.get_tensor(c_output[0]["index"])[0]
            pred_id = int(np.argmax(probs))
            confidence = probs[pred_id]

            if confidence >= CONFIDENCE_THRESHOLD:
                labels.append(CLASS_NAMES[pred_id])
            else:
                labels.append("neutral")

        from collections import Counter
        chunk_label = Counter(labels).most_common(1)[0][0]

        with label_lock:
            latest_chunk_label = chunk_label

        print(f"ML label → {chunk_label} | RMS={rms:.4f}")


# ======================================================
# MAIN
# ======================================================
print("\n🚼 Baby Monitor System Starting")
print("Press CTRL + C to stop\n")

with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32",
    callback=audio_callback,
):
    threading.Thread(target=ml_worker, daemon=True).start()
    threading.Thread(target=eye_worker, daemon=True).start()

    state = "NEUTRAL"

    cry_count = 0
    laugh_count = 0
    neutral_count = 0

    cry_switch_count = 0
    laugh_switch_count = 0

    last_baby_state = None
    last_emotion_state = None   # ⭐ NEW (important)

    print("🧠 State machine running\n")

    try:
        while True:
            time.sleep(1)

            with label_lock:
                label = latest_chunk_label

            # ----------------------------------
            # AUDIO COUNTERS
            # ----------------------------------
            if label == "cry":
                cry_count += 1
                laugh_count = neutral_count = 0

            elif label == "laugh":
                laugh_count += 1
                cry_count = neutral_count = 0

            else:
                neutral_count += 1
                cry_count = laugh_count = 0


            # ----------------------------------
            # STATE MACHINE
            # ----------------------------------
            if state == "NEUTRAL":

                cry_switch_count = 0
                laugh_switch_count = 0

                if cry_count >= ENTER_THRESHOLD:
                    state = "CRYING"

                elif laugh_count >= ENTER_THRESHOLD:
                    state = "LAUGHING"


            elif state == "CRYING":

                if label == "laugh":
                    laugh_switch_count += 1
                else:
                    laugh_switch_count = 0

                if laugh_switch_count >= SWITCH_THRESHOLD:
                    state = "LAUGHING"
                    cry_switch_count = laugh_switch_count = neutral_count = 0

                elif neutral_count >= EXIT_THRESHOLD:
                    state = "NEUTRAL"


            elif state == "LAUGHING":

                if label == "cry":
                    cry_switch_count += 1
                else:
                    cry_switch_count = 0

                if cry_switch_count >= SWITCH_THRESHOLD:
                    state = "CRYING"
                    cry_switch_count = laugh_switch_count = neutral_count = 0

                elif neutral_count >= EXIT_THRESHOLD:
                    state = "NEUTRAL"


            # ----------------------------------
            # LIGHT CONTROL (EMOTION ONLY)
            # ----------------------------------
            if state != last_emotion_state:

                if state == "LAUGHING":
                    print("💡 HAPPY MODE → Light ON")
                    light.on()
                else:
                    print("💡 NOT HAPPY → Light OFF")
                    light.off()

                last_emotion_state = state


            # ----------------------------------
            # EYE STATE
            # ----------------------------------
            eye_state = get_eye_state()

            if state == "CRYING":
                baby_state = "CRYING"
            elif state == "LAUGHING":
                baby_state = "LAUGHING"
            else:
                baby_state = "SLEEP" if eye_state == "CLOSED" else "AWAKE"


            print(
                f"label={label:<7} | "
                f"STATE={state:<8} | "
                f"EYES={eye_state:<6} | "
                f"BABY_STATE={baby_state}"
            )


            # ----------------------------------
            # AUDIO + SERVO ACTIONS
            # ----------------------------------
            if baby_state != last_baby_state:

                print(f"\n>>> BABY STATE → {baby_state}\n")

                if baby_state == "CRYING":
                    audio_player.play("soothing")
                    servo.start()

                elif baby_state == "LAUGHING":
                    audio_player.play("fun")
                    servo.stop()

                elif baby_state == "SLEEP":
                    audio_player.play("lullaby")
                    servo.stop()

                else:
                    audio_player.stop()
                    servo.stop()

                last_baby_state = baby_state


    except KeyboardInterrupt:
        print("\n🛑 Baby monitor stopped")

        servo.stop()
        light.off()
        light.cleanup()
