from smbus2 import SMBus


class I2CBus:
    """Thin wrapper around smbus2 for I2C communication."""

    def __init__(self, bus: int = 1):
        self._bus = SMBus(bus)

    def read_byte(self, address: int) -> int:
        return self._bus.read_byte(address)

    def read_byte_data(self, address: int, register: int) -> int:
        return self._bus.read_byte_data(address, register)

    def read_i2c_block_data(self, address: int, register: int, length: int) -> list[int]:
        return self._bus.read_i2c_block_data(address, register, length)

    def write_byte(self, address: int, value: int):
        self._bus.write_byte(address, value)

    def write_byte_data(self, address: int, register: int, value: int):
        self._bus.write_byte_data(address, register, value)

    def write_i2c_block_data(self, address: int, register: int, data: list[int]):
        self._bus.write_i2c_block_data(address, register, data)

    def close(self):
        self._bus.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
