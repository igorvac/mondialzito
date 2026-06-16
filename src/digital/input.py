from typing import Callable, Optional
import RPi.GPIO as GPIO


class DigitalInput:
    """Reads a digital input pin with optional interrupt callback."""

    def __init__(self, pin: int, pull_up: bool = True):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        pull = GPIO.PUD_UP if pull_up else GPIO.PUD_DOWN
        GPIO.setup(pin, GPIO.IN, pull_up_down=pull)

    def read(self) -> bool:
        return bool(GPIO.input(self.pin))

    def on_change(self, callback: Callable, edge: str = "both", bouncetime: int = 200):
        edge_map = {"rising": GPIO.RISING, "falling": GPIO.FALLING, "both": GPIO.BOTH}
        GPIO.add_event_detect(self.pin, edge_map[edge], callback=callback, bouncetime=bouncetime)

    def remove_callback(self):
        GPIO.remove_event_detect(self.pin)

    def cleanup(self):
        GPIO.cleanup(self.pin)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cleanup()
