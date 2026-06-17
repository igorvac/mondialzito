from unittest.mock import MagicMock, patch

from src.sensors.thermocouple import ThermocoupleReader, _SEEBECK_K

_GAIN = 100.0


def _make_reader(voltage=0.0, cpu_temp=25.0):
    mock_bus = MagicMock()
    reader = ThermocoupleReader(mock_bus, gain=_GAIN, window_size=1)
    reader._adc.read_voltage = MagicMock(return_value=voltage)
    reader._read_cpu_temp = MagicMock(return_value=cpu_temp)
    return reader


def test_read_returns_float():
    reader = _make_reader(voltage=0.1, cpu_temp=25.0)
    assert isinstance(reader.read(), float)


def test_zero_voltage_gives_cold_junction_temp():
    reader = _make_reader(voltage=0.0, cpu_temp=25.0)
    result = reader.read()
    assert abs(result - 25.0) < 1.0


def test_known_temperature():
    t_target, t_cj = 100.0, 25.0
    v_adc = (t_target - t_cj) * _SEEBECK_K * _GAIN
    reader = _make_reader(voltage=v_adc, cpu_temp=t_cj)
    # Kalman starts at 25°C; warm up with 50 identical readings before asserting
    for _ in range(50):
        result = reader.read()
    assert abs(result - t_target) < 2.0


def test_cold_junction_offset_applied():
    t_cj = 40.0
    reader = _make_reader(voltage=0.0, cpu_temp=t_cj)
    for _ in range(50):
        result = reader.read()
    assert abs(result - t_cj) < 2.0


def test_cpu_temp_fallback_on_oserror():
    mock_bus = MagicMock()
    reader = ThermocoupleReader(mock_bus, gain=_GAIN, window_size=1)
    reader._adc.read_voltage = MagicMock(return_value=0.0)
    with patch("builtins.open", side_effect=OSError):
        result = reader._read_cpu_temp()
    assert result == 25.0


def test_kalman_smoothing_reduces_spread():
    mock_bus = MagicMock()
    reader = ThermocoupleReader(mock_bus, gain=_GAIN, window_size=3)
    reader._read_cpu_temp = MagicMock(return_value=25.0)

    t_lo, t_hi = 90.0, 110.0
    v_lo = (t_lo - 25.0) * _SEEBECK_K * _GAIN
    v_hi = (t_hi - 25.0) * _SEEBECK_K * _GAIN

    results = []
    for v in [v_lo, v_hi] * 8:
        reader._adc.read_voltage = MagicMock(return_value=v)
        results.append(reader.read())

    spread = max(results[-6:]) - min(results[-6:])
    assert spread < (t_hi - t_lo)  # filter dampens raw 20°C swing
