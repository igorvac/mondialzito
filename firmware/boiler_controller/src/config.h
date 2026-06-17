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
// Sensor: LM35 OUT → A0 (único ADC do ESP8266, 0–1V)

// ── Sensor LM35 ───────────────────────────────────────────────────────────────
// Saída: 10 mV/°C → 0V = 0°C, 1V = 100°C
// Alimentação: 3.3V (não usar 5V — ADC do ESP8266 aceita no máximo 1V)
// Limite: leituras acima de 100°C saturam o ADC — use offset negativo se necessário
#define LM35_MV_PER_DEG 10.0f   // mV por grau Celsius

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
