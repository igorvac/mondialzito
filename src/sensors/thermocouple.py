import collections

from src.bus.i2c import I2CBus
from src.sensors.ads1115 import ADS1115
from src.sensors.kalman_filter import KalmanFilter

_SEEBECK_K = 41.276e-6  # V/°C — Type K Seebeck coefficient


class ThermocoupleReader:
    """
    Type K thermocouple reader via INA128 amplifier + ADS1115 ADC.

    Signal chain: thermocouple → INA128 (gain G) → ADS1115 AIN0 → I2C → RPi

    Temperature: T_hot = V_adc / (G × S_K) + T_cold_junction
    where T_cold_junction ≈ CPU die temperature (proxy for ambient at RPi GPIO header).
    """

    def __init__(
        self,
        bus: I2CBus,
        adc_address: int = 0x48,
        gain: float = 100.0,
        window_size: int = 5,
    ):
        self._adc = ADS1115(bus, adc_address)
        self._gain = gain
        self._kalman = KalmanFilter(Q=0.05, R=5.0)
        self._window: collections.deque = collections.deque(maxlen=window_size)

    def _read_cpu_temp(self) -> float:
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                return int(f.read().strip()) / 1000.0
        except OSError:
            return 25.0

    def read(self) -> float:
        v_adc = self._adc.read_voltage()
        t_cj = self._read_cpu_temp()
        t_raw = v_adc / (self._gain * _SEEBECK_K) + t_cj

        self._window.append(t_raw)
        t_avg = sum(self._window) / len(self._window)
        return self._kalman.update(t_avg)
