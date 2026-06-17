'use client';

import { useState, useEffect, useRef } from 'react';
import { supabase } from '@/lib/supabase';
import type { Settings } from '@/types';

interface Props {
  settings: Settings | null;
  onSettingsChange: (s: Settings) => void;
}

export default function Controls({ settings, onSettingsChange }: Props) {
  const [setpoint, setSetpoint] = useState(settings?.setpoint ?? 100);
  const [kp, setKp] = useState(settings?.kp ?? 1.0);
  const [ki, setKi] = useState(settings?.ki ?? 0.05);
  const [kd, setKd] = useState(settings?.kd ?? 0.1);
  const [cjOffset, setCjOffset] = useState(settings?.cj_offset ?? 0.0);
  const [pidSaved, setPidSaved] = useState(false);
  const spTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sincroniza quando settings externas mudam (ex: outro cliente)
  useEffect(() => {
    if (!settings) return;
    setSetpoint(settings.setpoint);
    setKp(settings.kp);
    setKi(settings.ki);
    setKd(settings.kd);
    setCjOffset(settings.cj_offset);
  }, [settings]);

  async function updateSettings(patch: Partial<Settings>) {
    const { data, error } = await supabase
      .from('settings')
      .update({ ...patch, updated_at: new Date().toISOString() })
      .eq('id', 1)
      .select()
      .single();
    if (!error && data) onSettingsChange(data as Settings);
  }

  function handleSlider(value: number) {
    setSetpoint(value);
    if (spTimerRef.current) clearTimeout(spTimerRef.current);
    spTimerRef.current = setTimeout(() => updateSettings({ setpoint: value }), 500);
  }

  async function handlePIDSubmit(e: React.FormEvent) {
    e.preventDefault();
    await updateSettings({ kp, ki, kd, cj_offset: cjOffset });
    setPidSaved(true);
    setTimeout(() => setPidSaved(false), 2000);
  }

  async function toggleRunning() {
    if (!settings) return;
    await updateSettings({ running: !settings.running });
  }

  const running = settings?.running ?? false;

  return (
    <div className="flex flex-col gap-3">

      {/* Setpoint */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
        <div className="text-[#8b949e] text-xs uppercase tracking-widest mb-3">
          Temperatura Alvo (Setpoint)
        </div>
        <div className="flex gap-2 items-center">
          <input
            type="range" min={0} max={300} step={1}
            value={setpoint}
            onChange={(e) => handleSlider(Number(e.target.value))}
            className="flex-1 accent-[#58a6ff]"
          />
          <input
            type="number" min={0} max={300}
            value={setpoint}
            onChange={(e) => {
              const v = Math.min(300, Math.max(0, Number(e.target.value)));
              setSetpoint(v);
              updateSettings({ setpoint: v });
            }}
            className="w-16 text-center bg-[#0d1117] border border-[#30363d] rounded px-2 py-1 text-sm"
          />
          <span className="text-[#8b949e] text-sm">°C</span>
        </div>
        <div className="text-center mt-2 text-[#58a6ff] font-bold text-lg">
          {setpoint} °C
        </div>
      </div>

      {/* PID */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
        <div className="text-[#8b949e] text-xs uppercase tracking-widest mb-3">
          Parâmetros PID
        </div>
        <form onSubmit={handlePIDSubmit} className="space-y-2">
          <div className="grid grid-cols-3 gap-2">
            {[
              { label: 'Kp', value: kp, set: setKp, step: 0.01 },
              { label: 'Ki', value: ki, set: setKi, step: 0.001 },
              { label: 'Kd', value: kd, set: setKd, step: 0.01 },
            ].map(({ label, value, set, step }) => (
              <div key={label}>
                <div className="text-[#8b949e] text-xs mb-1">{label}</div>
                <input
                  type="number" step={step} value={value}
                  onChange={(e) => set(parseFloat(e.target.value) || 0)}
                  className="w-full text-center bg-[#0d1117] border border-[#30363d] rounded px-2 py-1 text-sm"
                />
              </div>
            ))}
          </div>

          <div>
            <div className="text-[#8b949e] text-xs mb-1">Offset junta fria (°C)</div>
            <input
              type="number" step={0.5} value={cjOffset}
              onChange={(e) => setCjOffset(parseFloat(e.target.value) || 0)}
              className="w-full text-center bg-[#0d1117] border border-[#30363d] rounded px-2 py-1 text-sm"
            />
          </div>

          <button
            type="submit"
            className="w-full py-1.5 text-sm border border-[#30363d] rounded hover:bg-[#21262d] transition-colors"
          >
            Aplicar PID
          </button>
          {pidSaved && (
            <div className="text-center text-[#3fb950] text-xs">✓ Salvo</div>
          )}
        </form>
      </div>

      {/* Start / Stop */}
      <button
        onClick={toggleRunning}
        className={`w-full py-3 rounded-lg text-lg font-bold transition-colors ${
          running
            ? 'bg-[#da3633] hover:bg-[#b91c1c] text-white'
            : 'bg-[#238636] hover:bg-[#16a34a] text-white'
        }`}
      >
        {running ? '⏹ Parar' : '▶ Iniciar'}
      </button>

    </div>
  );
}
