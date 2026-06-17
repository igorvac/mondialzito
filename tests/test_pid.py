from unittest.mock import patch

from src.control.pid import PIDController


def _pid(**kwargs):
    defaults = dict(kp=1.0, ki=0.0, kd=0.0, setpoint=100.0, output_min=0.0, output_max=1.0)
    defaults.update(kwargs)
    return PIDController(**defaults)


def _monotonic_seq(*values):
    it = iter(values)
    return lambda: next(it)


def test_no_output_on_first_call():
    pid = _pid()
    with patch("src.control.pid.time.monotonic", _monotonic_seq(0.0)):
        assert pid.update(50.0) == 0.0


def test_proportional_only():
    pid = _pid(kp=0.05, ki=0.0, kd=0.0, output_max=10.0)
    with patch("src.control.pid.time.monotonic", _monotonic_seq(0.0, 1.0)):
        pid.update(80.0)
        out = pid.update(80.0)  # error=20, P=0.05*20=1.0
    assert abs(out - 1.0) < 1e-6


def test_proportional_clamped():
    pid = _pid(kp=10.0, ki=0.0, kd=0.0, output_max=1.0)
    with patch("src.control.pid.time.monotonic", _monotonic_seq(0.0, 1.0)):
        pid.update(80.0)
        out = pid.update(80.0)  # P=200 → clamped to 1.0
    assert out == 1.0


def test_integral_accumulates():
    pid = _pid(kp=0.0, ki=0.1, kd=0.0, output_max=100.0)
    seq = [0.0, 1.0, 2.0, 3.0]
    with patch("src.control.pid.time.monotonic", _monotonic_seq(*seq)):
        pid.update(90.0)
        out1 = pid.update(90.0)
        out2 = pid.update(90.0)
    assert out2 > out1 > 0.0


def test_anti_windup_caps_integral():
    pid = _pid(kp=0.0, ki=10.0, kd=0.0, output_max=1.0)
    times = [float(i) for i in range(20)]
    with patch("src.control.pid.time.monotonic", _monotonic_seq(*times)):
        for _ in range(19):
            pid.update(0.0)
    assert pid._integral <= 1.0 + 1e-9


def test_derivative_no_kick_on_setpoint_change():
    pid = _pid(kp=0.0, ki=0.0, kd=10.0, setpoint=100.0, output_max=100.0)
    with patch("src.control.pid.time.monotonic", _monotonic_seq(0.0, 1.0, 2.0)):
        pid.update(90.0)
        out_before = pid.update(90.0)  # measurement stable → D≈0
        pid.setpoint = 150.0
        out_after = pid.update(90.0)   # measurement still 90 → D still ≈0
    assert abs(out_before - out_after) < 0.01


def test_reset_clears_state():
    pid = _pid(kp=1.0, ki=1.0, kd=0.0, output_max=100.0)
    with patch("src.control.pid.time.monotonic", _monotonic_seq(0.0, 1.0, 2.0)):
        pid.update(50.0)
        pid.update(50.0)
    pid.reset()
    assert pid._integral == 0.0
    assert pid._prev_time is None
    assert pid._prev_measurement is None


def test_negative_error_clamped_to_min():
    pid = _pid(kp=1.0, ki=0.0, kd=0.0, setpoint=50.0, output_min=0.0)
    with patch("src.control.pid.time.monotonic", _monotonic_seq(0.0, 1.0)):
        pid.update(100.0)
        out = pid.update(100.0)  # error=-50, P=-50 → clamped to 0.0
    assert out == 0.0
