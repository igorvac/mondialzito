#pragma once

class KalmanFilter {
public:
    KalmanFilter(float Q = 0.05f, float R = 5.0f, float initial = 25.0f)
        : m_x(initial), m_P(1.0f), m_Q(Q), m_R(R) {}

    float update(float measurement) {
        m_P += m_Q;
        float K = m_P / (m_P + m_R);
        m_x   += K * (measurement - m_x);
        m_P   *= (1.0f - K);
        return m_x;
    }

    void reset(float value = 25.0f) {
        m_x = value;
        m_P = 1.0f;
    }

private:
    float m_x, m_P, m_Q, m_R;
};
