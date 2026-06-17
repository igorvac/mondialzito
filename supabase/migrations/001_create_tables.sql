-- Tabela de leituras do sensor (append-only, NodeMCU insere via REST)
CREATE TABLE IF NOT EXISTS readings (
  id          BIGSERIAL PRIMARY KEY,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  temperature DOUBLE PRECISION NOT NULL,
  setpoint    DOUBLE PRECISION NOT NULL,
  ssr_on      BOOLEAN NOT NULL,
  pid_output  DOUBLE PRECISION NOT NULL
);

-- Índice para consultas por data (histórico, gráfico)
CREATE INDEX IF NOT EXISTS idx_readings_created_at ON readings (created_at DESC);

-- Configurações do controlador (linha única, dashboard edita)
CREATE TABLE IF NOT EXISTS settings (
  id         INT PRIMARY KEY DEFAULT 1,
  setpoint   DOUBLE PRECISION NOT NULL DEFAULT 100.0,
  kp         DOUBLE PRECISION NOT NULL DEFAULT 1.0,
  ki         DOUBLE PRECISION NOT NULL DEFAULT 0.05,
  kd         DOUBLE PRECISION NOT NULL DEFAULT 0.1,
  cj_offset  DOUBLE PRECISION NOT NULL DEFAULT 0.0,
  running    BOOLEAN NOT NULL DEFAULT false,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Garante que sempre existe exatamente 1 linha de settings
INSERT INTO settings (id) VALUES (1)
  ON CONFLICT (id) DO NOTHING;

-- ── RLS (Row Level Security) ──────────────────────────────────────────────────
ALTER TABLE readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

-- Permite leitura pública anônima (para o dashboard e o NodeMCU)
CREATE POLICY "anon select readings"
  ON readings FOR SELECT
  TO anon USING (true);

CREATE POLICY "anon select settings"
  ON settings FOR SELECT
  TO anon USING (true);

-- Permite o NodeMCU inserir leituras com a chave anon
CREATE POLICY "anon insert readings"
  ON readings FOR INSERT
  TO anon WITH CHECK (true);

-- Permite o dashboard atualizar settings com a chave anon
CREATE POLICY "anon update settings"
  ON settings FOR UPDATE
  TO anon USING (true) WITH CHECK (true);

-- Habilita Realtime para as duas tabelas
ALTER PUBLICATION supabase_realtime ADD TABLE readings;
ALTER PUBLICATION supabase_realtime ADD TABLE settings;
