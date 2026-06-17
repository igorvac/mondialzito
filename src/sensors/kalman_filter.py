class KalmanFilter:
    """Scalar 1D Kalman filter for temperature noise reduction."""

    def __init__(self, Q: float = 0.05, R: float = 5.0, initial_estimate: float = 25.0):
        self._x = initial_estimate
        self._P = 1.0
        self._Q = Q
        self._R = R

    def update(self, measurement: float) -> float:
        self._P += self._Q
        K = self._P / (self._P + self._R)
        self._x += K * (measurement - self._x)
        self._P *= 1.0 - K
        return self._x
