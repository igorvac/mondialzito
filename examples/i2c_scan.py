"""Scan the I2C bus and print all detected device addresses."""
from src.bus.i2c import I2CBus

with I2CBus(bus=1) as bus:
    print("Scanning I2C bus 1...")
    found = []
    for addr in range(0x03, 0x78):
        try:
            bus.read_byte(addr)
            found.append(hex(addr))
        except OSError:
            pass
    print("Devices found:", found if found else "none")
