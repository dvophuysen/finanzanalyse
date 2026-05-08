import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Finanzanalyse",
  description: "Selbst-gehostetes, KI-gestütztes Haushaltsbuch",
};

const nav = [
  { href: ".", label: "Dashboard" },
  { href: "transactions", label: "Transaktionen" },
  { href: "import", label: "Import" },
  { href: "goals", label: "Ziele" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body>
        <div className="min-h-screen flex flex-col">
          <header className="border-b border-slate-200 dark:border-slate-800">
            <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-6">
              <span className="font-semibold text-lg">Finanzanalyse</span>
              <nav className="flex gap-4 text-sm">
                {nav.map((n) => (
                  <a key={n.href} href={n.href} className="hover:underline">
                    {n.label}
                  </a>
                ))}
              </nav>
            </div>
          </header>
          <main className="max-w-6xl mx-auto w-full px-4 py-6 flex-1">{children}</main>
        </div>
      </body>
    </html>
  );
}
