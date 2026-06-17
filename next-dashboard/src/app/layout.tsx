import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Controlador de Temperatura',
  description: 'Dashboard de controle de temperatura da caldeira',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
