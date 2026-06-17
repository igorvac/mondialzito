#pragma once

// ── WiFi ─────────────────────────────────────────────────────────────────────
#define WIFI_SSID       "SEU_WIFI_AQUI"
#define WIFI_PASSWORD   "SUA_SENHA_AQUI"

// ── Supabase ──────────────────────────────────────────────────────────────────
// Preencha com os valores do seu projeto em https://supabase.com/dashboard
#define SUPABASE_URL    "https://XXXXXXXXXXXXXXXX.supabase.co"
#define SUPABASE_ANON   "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.XXXXXXX"

// ── Pinos ─────────────────────────────────────────────────────────────────────
#define SSR_PIN         5     // D1 no NodeMCU v3 → GPIO5
#define ADC_PIN         17    // A0 no ESP8266 = GPIO17 internamente

// ── Circuito de amplificação (LM358) ─────────────────────────────────────────
// Ganho = 1 + Rf/Rg = 23  (Rf=22kΩ, Rg=1kΩ)
// Faixa de saída: 0–1 V para ~400°C (considerando cold junction 25°C)
#define AMP_GAIN        23.0f

// ── Termopar Tipo K ───────────────────────────────────────────────────────────
#define SEEBECK_K       41.276e-6f  // V/°C

// ── Tempos ────────────────────────────────────────────────────────────────────
#define LOOP_INTERVAL_MS      100   // leitura ADC + PID (10 Hz)
#define SSR_CYCLE_MS          2000  // ciclo time-proportioning do SSR (2 s)
#define REPORT_INTERVAL_MS    15000 // envio ao Supabase (15 s)
#define POLL_INTERVAL_MS      30000 // polling de settings (30 s)
#define SSR_DEADBAND_MS       50    // pulso mínimo do SSR (proteção zero-crossing)

// ── Filtro ────────────────────────────────────────────────────────────────────
#define KALMAN_Q        0.05f
#define KALMAN_R        5.0f
#define MA_WINDOW       5
