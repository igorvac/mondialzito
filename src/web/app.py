import json
import threading
import time
from collections import deque
from dataclasses import dataclass, field

from flask import Flask, Response, jsonify, render_template, request, stream_with_context

from src.control.pid import PIDController


@dataclass
class ControllerState:
    temperature: float = 0.0
    setpoint: float = 100.0
    ssr_fraction: float = 0.0
    ssr_on: bool = False
    running: bool = False
    history: deque = field(default_factory=lambda: deque(maxlen=3600))


def create_app(
    state: ControllerState,
    state_lock: threading.Lock,
    pid: PIDController,
    on_start,
    on_stop,
) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/stream")
    def stream():
        def event_stream():
            while True:
                with state_lock:
                    data = {
                        "temp": round(state.temperature, 2),
                        "setpoint": state.setpoint,
                        "ssr": state.ssr_on,
                        "running": state.running,
                        "ts": time.time(),
                    }
                yield f"data: {json.dumps(data)}\n\n"
                time.sleep(1.0)

        return Response(
            stream_with_context(event_stream()),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.route("/history")
    def history():
        with state_lock:
            data = list(state.history)
        step = max(1, len(data) // 360)
        return jsonify(data[::step])

    @app.route("/setpoint", methods=["POST"])
    def set_setpoint():
        body = request.get_json(force=True)
        sp = float(body.get("setpoint", state.setpoint))
        sp = max(0.0, min(300.0, sp))
        with state_lock:
            state.setpoint = sp
        pid.setpoint = sp
        return jsonify({"setpoint": sp})

    @app.route("/pid", methods=["POST"])
    def set_pid():
        body = request.get_json(force=True)
        pid.kp = float(body["kp"])
        pid.ki = float(body["ki"])
        pid.kd = float(body["kd"])
        return jsonify({"kp": pid.kp, "ki": pid.ki, "kd": pid.kd})

    @app.route("/control", methods=["POST"])
    def control():
        action = request.get_json(force=True).get("action")
        if action == "start":
            on_start()
        elif action == "stop":
            on_stop()
        with state_lock:
            running = state.running
        return jsonify({"running": running})

    return app
