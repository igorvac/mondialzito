import threading

from src.digital.output import DigitalOutput

_MIN_ON_TIME = 0.05  # seconds — guard for zero-crossing SSR minimum pulse


class SSRController:
    """
    Solid State Relay controller using time-proportioning within a fixed cycle.

    A dedicated thread runs the on/off cycle. threading.Event.wait() keeps the thread
    sleeping between transitions so it wakes immediately on shutdown.
    """

    def __init__(self, pin: int = 17, cycle_time: float = 2.0):
        self._relay = DigitalOutput(pin=pin, active_high=True)
        self._cycle_time = cycle_time
        self._output_fraction = 0.0
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def set_output(self, fraction: float):
        with self._lock:
            self._output_fraction = max(0.0, min(1.0, fraction))

    def _run(self):
        while not self._stop_event.is_set():
            with self._lock:
                fraction = self._output_fraction

            on_time = fraction * self._cycle_time
            if on_time < _MIN_ON_TIME:
                on_time = 0.0
            off_time = self._cycle_time - on_time

            if on_time > 0:
                self._relay.on()
                self._stop_event.wait(timeout=on_time)

            if off_time > 0 and not self._stop_event.is_set():
                self._relay.off()
                self._stop_event.wait(timeout=off_time)

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self._cycle_time + 1.0)
        self._relay.off()
        self._relay.cleanup()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
