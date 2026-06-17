'use client';

import { useEffect, useState, useCallback } from 'react';
import { supabase } from '@/lib/supabase';
import TempChart from '@/components/TempChart';
import StatusCard from '@/components/StatusCard';
import Controls from '@/components/Controls';
import type { Reading, Settings } from '@/types';

const MAX_READINGS = 360;

export default function DashboardPage() {
  const [readings, setReadings]   = useState<Reading[]>([]);
  const [settings, setSettings]   = useState<Settings | null>(null);
  const [connected, setConnected] = useState(false);

  // Carrega histórico inicial (últimas 360 leituras)
  useEffect(() => {
    supabase
      .from('readings')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(MAX_READINGS)
      .then(({ data }) => {
        if (data) setReadings([...data].reverse() as Reading[]);
      });

    supabase
      .from('settings')
      .select('*')
      .eq('id', 1)
      .single()
      .then(({ data }) => {
        if (data) setSettings(data as Settings);
      });
  }, []);

  // Subscription real-time para novas leituras
  useEffect(() => {
    const channel = supabase
      .channel('readings-live')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'readings' },
        (payload) => {
          setReadings((prev) => {
            const next = [...prev, payload.new as Reading];
            return next.length > MAX_READINGS ? next.slice(-MAX_READINGS) : next;
          });
        }
      )
      .on(
        'postgres_changes',
        { event: 'UPDATE', schema: 'public', table: 'settings' },
        (payload) => {
          setSettings(payload.new as Settings);
        }
      )
      .subscribe((status) => {
        setConnected(status === 'SUBSCRIBED');
      });

    return () => { supabase.removeChannel(channel); };
  }, []);

  const handleSettingsChange = useCallback((s: Settings) => {
    setSettings(s);
  }, []);

  const latest = readings.at(-1) ?? null;

  return (
    <main className="min-h-screen p-4 md:p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-[#58a6ff]">
          Controlador de Temperatura — Caldeira
        </h1>
        <span className={`text-xs px-2 py-1 rounded-full ${
          connected
            ? 'bg-[#238636] text-white'
            : 'bg-[#30363d] text-[#8b949e]'
        }`}>
          {connected ? '● Ao vivo' : '○ Conectando...'}
        </span>
      </div>

      {/* Grid principal */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">

        {/* Gráfico — ocupa 2 colunas no desktop */}
        <div className="xl:col-span-2 flex flex-col gap-4">
          <TempChart readings={readings} />

          {/* Últimas leituras — mini tabela */}
          {readings.length > 0 && (
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 overflow-x-auto">
              <div className="text-[#8b949e] text-xs uppercase tracking-widest mb-2">
                Últimas 5 leituras
              </div>
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="text-[#8b949e] border-b border-[#30363d]">
                    <th className="pb-1 pr-4">Horário</th>
                    <th className="pb-1 pr-4">Temp (°C)</th>
                    <th className="pb-1 pr-4">Setpoint</th>
                    <th className="pb-1 pr-4">SSR</th>
                    <th className="pb-1">PID</th>
                  </tr>
                </thead>
                <tbody>
                  {[...readings].reverse().slice(0, 5).map((r) => (
                    <tr key={r.id} className="border-b border-[#21262d]">
                      <td className="py-1 pr-4 text-[#8b949e] text-xs">
                        {new Date(r.created_at).toLocaleTimeString('pt-BR')}
                      </td>
                      <td className="py-1 pr-4 text-[#f85149] font-mono">
                        {r.temperature.toFixed(2)}
                      </td>
                      <td className="py-1 pr-4 font-mono">{r.setpoint.toFixed(1)}</td>
                      <td className="py-1 pr-4">
                        <span className={`text-xs px-1.5 py-0.5 rounded ${
                          r.ssr_on ? 'bg-[#3fb950] text-black' : 'bg-[#484f58] text-white'
                        }`}>
                          {r.ssr_on ? 'ON' : 'OFF'}
                        </span>
                      </td>
                      <td className="py-1 font-mono text-xs">
                        {(r.pid_output * 100).toFixed(0)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Painel de controle */}
        <div className="flex flex-col gap-4">
          <StatusCard latest={latest} settings={settings} />
          <Controls settings={settings} onSettingsChange={handleSettingsChange} />
        </div>
      </div>
    </main>
  );
}
