'use client';

import type { Reading, Settings } from '@/types';

interface Props {
  latest: Reading | null;
  settings: Settings | null;
}

export default function StatusCard({ latest, settings }: Props) {
  const temp   = latest?.temperature ?? null;
  const ssrOn  = latest?.ssr_on ?? false;
  const running = settings?.running ?? false;

  return (
    <div className="flex flex-col gap-3">
      {/* Temperatura atual */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-center">
        <div className="text-[#8b949e] text-xs uppercase tracking-widest mb-1">
          Temperatura Atual
        </div>
        <div className="text-[#f85149] text-5xl font-bold leading-none">
          {temp !== null ? temp.toFixed(1) : '---'}
        </div>
        <div className="text-[#8b949e] text-lg">°C</div>
      </div>

      {/* Status SSR + rodando */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 flex items-center gap-3">
        <span
          className={`w-3.5 h-3.5 rounded-full flex-shrink-0 ${
            ssrOn
              ? 'bg-[#3fb950] shadow-[0_0_8px_#3fb950]'
              : 'bg-[#484f58]'
          }`}
        />
        <span className="font-mono text-sm">
          SSR: <strong>{ssrOn ? 'ON' : 'OFF'}</strong>
        </span>
        <span
          className={`ml-auto text-xs px-2 py-0.5 rounded-full ${
            running
              ? 'bg-[#238636] text-white'
              : 'bg-[#30363d] text-[#8b949e]'
          }`}
        >
          {running ? 'Controlando' : 'Parado'}
        </span>
      </div>
    </div>
  );
}
