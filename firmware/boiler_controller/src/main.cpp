/*
 * Controlador de temperatura para caldeira — NodeMCU v3 (ESP8266Mod)
 *
 * Circuito:
 *   Termopar Tipo K (+) → IN+ do LM358 → saída LM358 → A0
 *   Termopar Tipo K (−) → GND
 *   LM358: ganho = 24× (Rf=23kΩ, Rg=1kΩ), Vcc=3.3V, Vee=GND
 *   SSR controle: D1 (GPIO5), active HIGH
 *
 * Dependências (Library Manager do Arduino IDE):
 *   - ESP8266WiFi         (incluída na board ESP8266)
 *   - ESP8266HTTPClient   (incluída na board ESP8266)
 *   - WiFiClientSecureBearSSL (incluída na board ESP8266)
 *   - ArduinoJson 6.x
 *
 * Board: NodeMCU 1.0 (ESP-12E Module), 80MHz, Flash 4MB
 */

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecureBearSSL.h>
#include <ArduinoJson.h>

#include "config.h"
#include "kalman.h"
#include "pid.h"

#define WIFI_SSID     "deviceNetwork"
#define WIFI_PASSWORD "limaocravo"
#define SUPABASE_URL  "https://jhbkwdaxvjtrcyzeltlt.supabase.co"
#define SUPABASE_ANON "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpoYmt3ZGF4dmp0cmN5emVsdGx0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE3MTQ3OTMsImV4cCI6MjA5NzI5MDc5M30.4t8gN_GpsXq4BQLCEPRz7kMhjHyLGYS8qzQSPWvA-CI"  // Settings → API → anon key

// ── Estado global ─────────────────────────────────────────────────────────────
struct Settings {
    float  setpoint  = 100.0f;
    float  kp        = 1.0f;
    float  ki        = 0.05f;
    float  kd        = 0.1f;
    float  cj_offset = 0.0f;
    bool   running   = false;
};

Settings    g_settings;
KalmanFilter g_kalman(KALMAN_Q, KALMAN_R, 25.0f);
PIDController g_pid(1.0f, 0.05f, 0.1f);

float g_temperature  = 25.0f;
float g_pidOutput    = 0.0f;
bool  g_ssrOn        = false;

// Média móvel com array circular
float  g_maWindow[MA_WINDOW] = {};
int    g_maIdx = 0;
bool   g_maFull = false;

// Timers
unsigned long g_lastLoop   = 0;
unsigned long g_lastReport = 0;
unsigned long g_lastPoll   = 0;

// ── Funções de leitura ────────────────────────────────────────────────────────

float movingAverage(float value) {
    g_maWindow[g_maIdx] = value;
    g_maIdx = (g_maIdx + 1) % MA_WINDOW;
    if (g_maIdx == 0) g_maFull = true;

    int count = g_maFull ? MA_WINDOW : g_maIdx;
    float sum = 0;
    for (int i = 0; i < count; i++) sum += g_maWindow[i];
    return sum / count;
}

float readTemperature() {
    int raw     = analogRead(A0);                // 0–1023 (único ADC do ESP8266)
    float v_adc = raw / 1023.0f;                // 0.0–1.0 V
    float v_tc  = v_adc / AMP_GAIN;             // retira ganho do LM358
    float t_raw = v_tc / SEEBECK_K + (25.0f + g_settings.cj_offset);
    float t_avg = movingAverage(t_raw);
    Serial.printf("[ADC] raw=%d  v_adc=%.4fV  v_tc=%.4fmV\n",
                  raw, v_adc, v_tc * 1000.0f);
    return g_kalman.update(t_avg);
}

// ── Controle SSR (time-proportioning, sem threads) ────────────────────────────

void updateSSR(float fraction) {
    unsigned long cyclePos = millis() % (unsigned long)SSR_CYCLE_MS;
    unsigned long onTime   = (unsigned long)(fraction * SSR_CYCLE_MS);
    if (onTime < (unsigned long)SSR_DEADBAND_MS) onTime = 0;

    bool shouldBeOn = (onTime > 0 && cyclePos < onTime);
    if (shouldBeOn != g_ssrOn) {
        digitalWrite(SSR_PIN, shouldBeOn ? HIGH : LOW);
        g_ssrOn = shouldBeOn;
    }
}

// ── Supabase REST ─────────────────────────────────────────────────────────────

BearSSL::WiFiClientSecure g_tlsClient;

bool supabasePost(const String& path, const String& body) {
    HTTPClient http;
    g_tlsClient.setInsecure();  // MVP: sem validação de certificado

    if (!http.begin(g_tlsClient, String(SUPABASE_URL) + path)) {
        return false;
    }
    http.addHeader("Content-Type",  "application/json");
    http.addHeader("apikey",        SUPABASE_ANON);
    http.addHeader("Authorization", String("Bearer ") + SUPABASE_ANON);
    http.addHeader("Prefer",        "return=minimal");

    int code = http.POST(body);
    http.end();
    return (code >= 200 && code < 300);
}

String supabaseGet(const String& path) {
    HTTPClient http;
    g_tlsClient.setInsecure();

    if (!http.begin(g_tlsClient, String(SUPABASE_URL) + path)) {
        return "";
    }
    http.addHeader("apikey",        SUPABASE_ANON);
    http.addHeader("Authorization", String("Bearer ") + SUPABASE_ANON);

    int code = http.GET();
    String body = (code == 200) ? http.getString() : "";
    http.end();
    return body;
}

void reportReading() {
    StaticJsonDocument<128> doc;
    doc["temperature"] = g_temperature;
    doc["setpoint"]    = g_settings.setpoint;
    doc["ssr_on"]      = g_ssrOn;
    doc["pid_output"]  = g_pidOutput;

    String body;
    serializeJson(doc, body);

    bool ok = supabasePost("/rest/v1/readings", body);
    Serial.printf("[Supabase] POST readings: %s\n", ok ? "OK" : "FAIL");
}

void pollSettings() {
    String resp = supabaseGet("/rest/v1/settings?id=eq.1&limit=1");
    if (resp.isEmpty()) {
        Serial.println("[Supabase] GET settings: FAIL");
        return;
    }

    StaticJsonDocument<256> doc;
    if (deserializeJson(doc, resp) != DeserializationError::Ok) return;
    JsonArray arr = doc.as<JsonArray>();
    if (arr.size() == 0) return;

    JsonObject s = arr[0];
    bool wasRunning = g_settings.running;

    g_settings.setpoint  = s["setpoint"]  | g_settings.setpoint;
    g_settings.kp        = s["kp"]        | g_settings.kp;
    g_settings.ki        = s["ki"]        | g_settings.ki;
    g_settings.kd        = s["kd"]        | g_settings.kd;
    g_settings.cj_offset = s["cj_offset"] | g_settings.cj_offset;
    g_settings.running   = s["running"]   | g_settings.running;

    // Atualiza ganhos do PID
    g_pid.kp = g_settings.kp;
    g_pid.ki = g_settings.ki;
    g_pid.kd = g_settings.kd;

    // Reinicia PID se passou de parado → rodando
    if (!wasRunning && g_settings.running) {
        g_pid.reset();
        g_kalman.reset(g_temperature);
    }

    Serial.printf("[Supabase] Settings: sp=%.1f kp=%.3f ki=%.4f kd=%.3f run=%d\n",
        g_settings.setpoint, g_settings.kp, g_settings.ki, g_settings.kd,
        g_settings.running);
}

// ── Setup ─────────────────────────────────────────────────────────────────────

void setup() {
    Serial.begin(115200);
    Serial.println("\n[Boot] Controlador de temperatura iniciando...");

    pinMode(SSR_PIN, OUTPUT);
    digitalWrite(SSR_PIN, LOW);  // SSR desligado no boot

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("[WiFi] Conectando");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print('.');
    }
    Serial.printf("\n[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());

    // Busca configurações iniciais antes do primeiro loop
    pollSettings();

    g_lastLoop   = millis();
    g_lastReport = millis();
    g_lastPoll   = millis();
}

// ── Loop principal ────────────────────────────────────────────────────────────

void loop() {
    unsigned long now = millis();

    // 10 Hz: leitura + PID + SSR
    if (now - g_lastLoop >= (unsigned long)LOOP_INTERVAL_MS) {
        g_lastLoop = now;

        g_temperature = readTemperature();

        if (g_settings.running) {
            g_pidOutput = g_pid.update(g_temperature, g_settings.setpoint);
        } else {
            g_pidOutput = 0.0f;
            g_pid.reset();
        }

        updateSSR(g_pidOutput);

        Serial.printf("[Loop] T=%.2f°C  SP=%.1f  PID=%.3f  SSR=%s\n",
            g_temperature, g_settings.setpoint, g_pidOutput,
            g_ssrOn ? "ON" : "OFF");
    }

    // 15s: envia leitura ao Supabase
    if (now - g_lastReport >= (unsigned long)REPORT_INTERVAL_MS) {
        g_lastReport = now;
        reportReading();
    }

    // 30s: busca settings atualizadas
    if (now - g_lastPoll >= (unsigned long)POLL_INTERVAL_MS) {
        g_lastPoll = now;
        pollSettings();
    }

    // Pequena pausa para o watchdog do ESP8266 não resetar
    yield();
}
