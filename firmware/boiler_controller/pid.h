#pragma once

class PIDController {
public:
    PIDController(float kp, float ki, float kd,
                  float outMin = 0.0f, float outMax = 1.0f)
        : kp(kp), ki(ki), kd(kd),
          _outMin(outMin), _outMax(outMax),
          _integral(0), _prevMeas(0),
          _firstCall(true), _prevMs(0) {}

    float update(float measurement, float setpoint) {
        unsigned long now = millis();
        if (_firstCall) {
            _firstCall = false;
            _prevMeas  = measurement;
            _prevMs    = now;
            return 0.0f;
        }

        float dt = (now - _prevMs) / 1000.0f;
        if (dt <= 0) return 0.0f;

        float error = setpoint - measurement;
        float p     = kp * error;
        _integral  += ki * error * dt;
        // derivativo na medição: evita kick ao mudar setpoint
        float d     = -kd * (measurement - _prevMeas) / dt;
        float out   = p + _integral + d;

        // anti-windup por back-calculation
        if (out > _outMax) {
            _integral = _outMax - p - d;
            out = _outMax;
        } else if (out < _outMin) {
            _integral = _outMin - p - d;
            out = _outMin;
        }

        _prevMeas = measurement;
        _prevMs   = now;
        return out;
    }

    void reset() {
        _integral  = 0;
        _firstCall = true;
    }

    float kp, ki, kd;

private:
    float        _outMin, _outMax;
    float        _integral, _prevMeas;
    bool         _firstCall;
    unsigned long _prevMs;
};
