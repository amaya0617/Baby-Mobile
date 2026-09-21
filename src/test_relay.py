import time
import RPi.GPIO as GPIO

PIN = 23   # the GPIO pin your relay IN is connected to

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

print("Relay test starting...")

while True:
    print("GPIO HIGH")
    GPIO.output(PIN, GPIO.HIGH)
    time.sleep(3)

    print("GPIO LOW")
    GPIO.output(PIN, GPIO.LOW)
    time.sleep(3)
