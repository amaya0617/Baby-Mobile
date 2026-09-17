# src/servo_controller.py

import threading
import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️ RPi.GPIO not found — servo simulation mode")


class ServoController:
    """
    Stable MG995 servo controller
    """

    def __init__(self, pin=18, freq=50):
        self.pin = pin
        self.freq = freq

        self._running = False
        self._stop_event = threading.Event()
        self._thread = None

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            self.pwm = GPIO.PWM(self.pin, self.freq)
            self.pwm.start(0)
            print(f"✅ MG995 initialized on GPIO {self.pin}")
        else:
            self.pwm = None

    def _angle_to_duty(self, angle):
        return 2.5 + (angle / 180.0) * 10

    def _run(self):
        print("🔄 Servo running")

        min_angle = 0
        max_angle = 180

        angle = min_angle
        direction = 1

        STEP = 5
        MOVE_DELAY = 0.10

        while not self._stop_event.is_set():

            duty = self._angle_to_duty(angle)

            if GPIO_AVAILABLE:
                self.pwm.ChangeDutyCycle(duty)
            else:
                print(f"🌀 angle={angle}")

            angle += direction * STEP

            if angle >= max_angle:
                angle = max_angle
                direction = -1
            elif angle <= min_angle:
                angle = min_angle
                direction = 1

            time.sleep(MOVE_DELAY)

        print("⏹ Servo stopped")

    def start(self):
        if self._running:
            return

        self._stop_event.clear()

        # restart PWM cleanly
        if GPIO_AVAILABLE:
            self.pwm.start(0)

        self._thread = threading.Thread(
            target=self._run,
            daemon=True
        )
        self._thread.start()

        self._running = True
        print("▶️ Servo STARTED")

    def stop(self):
        if not self._running:
            return

        self._stop_event.set()
        self._running = False

        if GPIO_AVAILABLE:
            self.pwm.ChangeDutyCycle(0)   # ✅ removes jitter
            # DO NOT hold angle

        print("⏹ Servo STOPPED")

    def cleanup(self):
        if GPIO_AVAILABLE:
            self.pwm.stop()
            GPIO.cleanup()
            print("🧹 GPIO cleaned")
