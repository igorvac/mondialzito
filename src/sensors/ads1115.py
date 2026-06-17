import time

from src.bus.i2c import I2CBus

_REG_CONVERSION = 0x00
_REG_CONFIG = 0x01

# Single-shot, AIN0-GND, PGA ±2.048 V, 128 SPS, comparator disabled
# MSB: OS=1, MUX=100(AIN0-GND), PGA=010(±2.048V), MODE=1
# LSB: DR=100(128SPS), COMP defaults, COMP_QUE=11(disable)
_CFG_MSB = 0xC5
_CFG_LSB = 0x83
_LSB_V = 2.048 / 32768  # volts per LSB for ±2.048 V range


class ADS1115:
    """ADS1115 16-bit ADC driver over I2C, single-ended AIN0."""

    def __init__(self, bus: I2CBus, address: int = 0x48):
        self._bus = bus
        self._addr = address

    def _start_conversion(self):
        self._bus.write_i2c_block_data(self._addr, _REG_CONFIG, [_CFG_MSB, _CFG_LSB])

    def _ready(self) -> bool:
        data = self._bus.read_i2c_block_data(self._addr, _REG_CONFIG, 2)
        return bool((data[0] >> 7) & 1)

    def read_raw(self) -> int:
        self._start_conversion()
        time.sleep(0.008)  # 128 SPS → ~7.8 ms per conversion
        deadline = time.monotonic() + 0.05
        while not self._ready():
            if time.monotonic() > deadline:
                raise TimeoutError("ADS1115 conversion timed out")
            time.sleep(0.001)
        data = self._bus.read_i2c_block_data(self._addr, _REG_CONVERSION, 2)
        raw = (data[0] << 8) | data[1]
        if raw > 32767:
            raw -= 65536
        return raw

    def read_voltage(self) -> float:
        return self.read_raw() * _LSB_V
