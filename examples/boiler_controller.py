"""
Controlador de temperatura para caldeira — Raspberry Pi 3B
=========================================================

Uso:
    python -m examples.boiler_controller [--setpoint 120] [--port 5000]

Hardware:
    Termopar Tipo K → INA128 (ganho 100×) → ADS1115 (I2C 0x48) → BCM2/3
    SSR controle → GPIO BCM17 (active HIGH)

Interface web:
    http://<ip-do-rpi>:5000
"""

import argparse
import logging
import threading
import time

from src.bus.i2c import I2CBus
from src.control.pid import PIDController
from src.control.ssr import SSRController
from src.sensors.thermocouple import ThermocoupleReader
from src.web.app import ControllerState, create_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Controlador de temperatura de caldeira")
    parser.add_argument("--setpoint", type=float, default=100.0, help="Temperatura alvo em °C")
    parser.add_argument("--kp", type=float, default=1.0)
    parser.add_argument("--ki", type=float, default=0.05)
    parser.add_argument("--kd", type=float, default=0.1)
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--ssr-pin", type=int, default=17)
    args = parser.parse_args()

    state = ControllerState(setpoint=args.setpoint)
    state_lock = threading.Lock()
    stop_event = threading.Event()

    pid = PIDController(
        kp=args.kp, ki=args.ki, kd=args.kd,
        setpoint=args.setpoint,
    )

    def on_start():
        pid.reset()
        with state_lock:
            state.running = True
        log.info("Controle iniciado — setpoint=%.1f°C", state.setpoint)

    def on_stop():
        with state_lock:
            state.running = False
        log.info("Controle parado")

    with I2CBus(bus=1) as i2c:
        sensor = ThermocoupleReader(i2c)

        with SSRController(pin=args.ssr_pin) as ssr:

            def control_loop():
                while not stop_event.is_set():
                    t0 = time.monotonic()

                    try:
                        temp = sensor.read()
                    except Exception as exc:
                        log.warning("Erro na leitura do sensor: %s", exc)
                        stop_event.wait(timeout=0.1)
                        continue

                    with state_lock:
                        running = state.running

                    fraction = pid.update(temp) if running else 0.0
                    ssr.set_output(fraction)

                    with state_lock:
                        state.temperature = temp
                        state.ssr_fraction = fraction
                        state.ssr_on = fraction >= 0.025
                        state.history.append({
                            "ts": time.time(),
                            "temp": round(temp, 2),
                            "setpoint": state.setpoint,
                            "ssr": state.ssr_on,
                        })

                    elapsed = time.monotonic() - t0
                    stop_event.wait(timeout=max(0.0, 0.1 - elapsed))

            loop = threading.Thread(target=control_loop, daemon=True)
            loop.start()
            log.info("Loop de controle iniciado (10 Hz)")
            log.info("Interface web disponível em http://0.0.0.0:%d", args.port)

            app = create_app(state, state_lock, pid, on_start, on_stop)
            try:
                app.run(host="0.0.0.0", port=args.port, threaded=True, use_reloader=False)
            except KeyboardInterrupt:
                log.info("Encerrando...")
            finally:
                stop_event.set()
                loop.join(timeout=2.0)


if __name__ == "__main__":
    main()
