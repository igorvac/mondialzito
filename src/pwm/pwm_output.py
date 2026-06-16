import RPi.GPIO as GPIO


class PWMOutput:
    """Hardware-backed PWM output for motors, servos, and dimmers."""

    def __init__(self, pin: int, frequency: float = 1000.0):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self._pwm = GPIO.PWM(pin, frequency)
        self._duty = 0.0
        self._pwm.start(0)

    @property
    def duty_cycle(self) -> float:
        return self._duty

    @duty_cycle.setter
    def duty_cycle(self, value: float):
        self._duty = max(0.0, min(100.0, value))
        self._pwm.ChangeDutyCycle(self._duty)

    def set_frequency(self, frequency: float):
        self._pwm.ChangeFrequency(frequency)

    # Servo helpers (50 Hz, 1–2 ms pulse → 2.5–12.5 % duty)
    def set_servo_angle(self, angle: float):
        duty = 2.5 + (angle / 180.0) * 10.0
        self.duty_cycle = duty

    def stop(self):
        self._pwm.stop()

    def cleanup(self):
        self.stop()
        GPIO.cleanup(self.pin)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cleanup()
