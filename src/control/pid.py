import time


class PIDController:
    """
    PID controller with anti-windup (back-calculation) and derivative on measurement.

    Derivative on measurement avoids output spikes when setpoint changes at runtime.
    Anti-windup prevents integral from growing unbounded while output is saturated.
    """

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        setpoint: float,
        output_min: float = 0.0,
        output_max: float = 1.0,
    ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self._output_min = output_min
        self._output_max = output_max
        self._integral = 0.0
        self._prev_measurement: float | None = None
        self._prev_time: float | None = None

    def update(self, measurement: float) -> float:
        now = time.monotonic()
        if self._prev_time is None:
            self._prev_time = now
            self._prev_measurement = measurement
            return 0.0

        dt = now - self._prev_time
        if dt <= 0:
            return 0.0

        error = self.setpoint - measurement
        p = self.kp * error
        self._integral += self.ki * error * dt
        d = -self.kd * (measurement - self._prev_measurement) / dt  # type: ignore[operator]

        output = p + self._integral + d

        if output > self._output_max:
            self._integral = self._output_max - p - d
            output = self._output_max
        elif output < self._output_min:
            self._integral = self._output_min - p - d
            output = self._output_min

        self._prev_measurement = measurement
        self._prev_time = now
        return output

    def reset(self):
        self._integral = 0.0
        self._prev_measurement = None
        self._prev_time = None
