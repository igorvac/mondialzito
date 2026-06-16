# mondialzito — Raspberry Pi GPIO Project

## Setup (no Raspberry Pi)
```bash
pip install -r requirements-dev.txt
pytest
```

## Setup (no Raspberry Pi)
```bash
pip install -r requirements.txt
```

## Running examples
```bash
python -m examples.blink
python -m examples.servo
python -m examples.i2c_scan
```

## Project structure
- `src/digital/` — saída/entrada digital (LEDs, relés, botões)
- `src/pwm/`     — PWM (motores DC, servos, dimmers)
- `src/bus/`     — protocolos de comunicação (I2C, SPI, UART)
- `src/sensors/` — drivers de sensores (adicionar aqui)
- `examples/`    — scripts prontos para testar no hardware
- `tests/`       — testes unitários com mock de GPIO

## Pin numbering
Todos os pinos usam **BCM** (Broadcom), não o número físico do conector.
