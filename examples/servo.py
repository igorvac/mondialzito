"""Sweep a servo connected to GPIO 18 (BCM) from 0° to 180° and back."""
import time
from src.pwm.pwm_output import PWMOutput

with PWMOutput(pin=18, frequency=50) as servo:
    for angle in list(range(0, 181, 10)) + list(range(180, -1, -10)):
        servo.set_servo_angle(angle)
        time.sleep(0.05)
