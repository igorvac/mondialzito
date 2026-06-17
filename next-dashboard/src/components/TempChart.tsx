'use client';

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import type { Reading } from '@/types';

interface Props {
  readings: Reading[];
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString('pt-BR', {
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  });
}

export default function TempChart({ readings }: Props) {
  const data = readings.map((r) => ({
    time:        formatTime(r.created_at),
    temperatura: parseFloat(r.temperature.toFixed(2)),
    setpoint:    parseFloat(r.setpoint.toFixed(1)),
  }));

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
          <XAxis
            dataKey="time"
            tick={{ fill: '#8b949e', fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: '#8b949e', fontSize: 11 }}
            domain={['auto', 'auto']}
            unit="°C"
          />
          <Tooltip
            contentStyle={{ background: '#161b22', border: '1px solid #30363d', color: '#c9d1d9' }}
            labelStyle={{ color: '#8b949e' }}
          />
          <Legend wrapperStyle={{ color: '#c9d1d9', fontSize: 12 }} />
          <Line
            type="monotone"
            dataKey="temperatura"
            stroke="#f85149"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="setpoint"
            stroke="#58a6ff"
            strokeWidth={1.5}
            strokeDasharray="6 3"
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
