import serial


class UARTBus:
    """Serial/UART communication wrapper."""

    def __init__(self, port: str = "/dev/serial0", baudrate: int = 9600, timeout: float = 1.0):
        self._serial = serial.Serial(port, baudrate=baudrate, timeout=timeout)

    def write(self, data: bytes):
        self._serial.write(data)

    def read(self, size: int = 1) -> bytes:
        return self._serial.read(size)

    def readline(self) -> bytes:
        return self._serial.readline()

    def available(self) -> int:
        return self._serial.in_waiting

    def flush(self):
        self._serial.flush()

    def close(self):
        self._serial.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
