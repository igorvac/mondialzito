"""Blink an LED connected to GPIO 17 (BCM) at 1 Hz."""
import time
from src.digital.output import DigitalOutput

with DigitalOutput(pin=17) as led:
    for _ in range(10):
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)
