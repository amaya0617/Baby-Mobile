try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️ GPIO not available – light in simulation mode")


class LightController:
    def __init__(self, pin=23):
        self.pin = pin
        self._state = False

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)

            # Relay OFF at startup
            GPIO.output(self.pin, GPIO.HIGH)

            print(f"💡 Light controller ready on GPIO {self.pin}")

    def on(self):
        if self._state:
            return

        if GPIO_AVAILABLE:
            GPIO.output(self.pin, GPIO.LOW)   # LOW = ON
        else:
            print("💡 [SIM] Light ON")

        self._state = True
        print("💡 Light ON")

    def off(self):
        if not self._state:
            return

        if GPIO_AVAILABLE:
            GPIO.output(self.pin, GPIO.HIGH)  # HIGH = OFF
        else:
            print("💡 [SIM] Light OFF")

        self._state = False
        print("💡 Light OFF")
