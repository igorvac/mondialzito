"""
Pytest conftest: register RPi.GPIO and smbus2 stubs for non-Pi environments.
Runs before any test imports so hardware-dependent modules can be imported safely.
"""
import sys
from unittest.mock import MagicMock

def _stub_module(name):
    if name not in sys.modules:
        sys.modules[name] = MagicMock()

# RPi.GPIO stub with realistic constants
_gpio = MagicMock()
_gpio.BCM = 11
_gpio.BOARD = 10
_gpio.OUT = 0
_gpio.IN = 1
_gpio.HIGH = 1
_gpio.LOW = 0
_gpio.PUD_UP = 22
_gpio.PUD_DOWN = 21
_gpio.RISING = 31
_gpio.FALLING = 32
_gpio.BOTH = 33

_rpi = MagicMock()
_rpi.GPIO = _gpio

sys.modules.setdefault("RPi", _rpi)
sys.modules.setdefault("RPi.GPIO", _gpio)

# smbus2 stub (used by I2CBus)
_stub_module("smbus2")

# spidev stub
_stub_module("spidev")
