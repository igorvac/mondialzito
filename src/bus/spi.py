import spidev


class SPIBus:
    """Wrapper around spidev for SPI communication."""

    def __init__(self, bus: int = 0, device: int = 0, max_speed_hz: int = 1_000_000):
        self._spi = spidev.SpiDev()
        self._spi.open(bus, device)
        self._spi.max_speed_hz = max_speed_hz
        self._spi.mode = 0

    def transfer(self, data: list[int]) -> list[int]:
        return self._spi.xfer2(data)

    def write(self, data: list[int]):
        self._spi.writebytes(data)

    def read(self, length: int) -> list[int]:
        return self._spi.readbytes(length)

    def close(self):
        self._spi.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
