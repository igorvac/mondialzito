import RPi.GPIO as GPIO


class DigitalOutput:
    """Controls a single digital output pin (LED, relay, etc.)."""

    def __init__(self, pin: int, active_high: bool = True):
        self.pin = pin
        self.active_high = active_high
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH if self.active_high else GPIO.LOW)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW if self.active_high else GPIO.HIGH)

    def toggle(self):
        current = GPIO.input(self.pin)
        GPIO.output(self.pin, not current)

    def cleanup(self):
        GPIO.cleanup(self.pin)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cleanup()
