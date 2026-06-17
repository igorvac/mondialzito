#pragma once

class KalmanFilter {
public:
    KalmanFilter(float Q = 0.05f, float R = 5.0f, float initial = 25.0f)
        : _x(initial), _P(1.0f), _Q(Q), _R(R) {}

    float update(float measurement) {
        _P += _Q;
        float K = _P / (_P + _R);
        _x   += K * (measurement - _x);
        _P   *= (1.0f - K);
        return _x;
    }

    void reset(float value = 25.0f) {
        _x = value;
        _P = 1.0f;
    }

private:
    float _x, _P, _Q, _R;
};
