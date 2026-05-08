"use client";

import useSWR from "swr";
import { fetcher, fmtEUR } from "@/lib/api";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type CashflowPoint = { period: string; income: string; expense: string; net: string };
type BreakdownItem = {
  category_id: number | null;
  category_name: string;
  amount: string;
  transactions: number;
};

export default function Dashboard() {
  const { data: cashflow } = useSWR<CashflowPoint[]>("/analytics/cashflow", fetcher);
  const { data: breakdown } = useSWR<BreakdownItem[]>("/analytics/breakdown", fetcher);

  const chartData =
    cashflow?.map((c) => ({
      period: c.period,
      Einnahmen: parseFloat(c.income),
      Ausgaben: parseFloat(c.expense),
      Netto: parseFloat(c.net),
    })) ?? [];

  const totalNet = cashflow?.reduce((s, c) => s + parseFloat(c.net), 0) ?? 0;
  const lastMonth = cashflow?.[cashflow.length - 1];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card title="Netto (12 Mo.)" value={fmtEUR(totalNet)} />
        <Card
          title="Letzter Monat – Einnahmen"
          value={lastMonth ? fmtEUR(parseFloat(lastMonth.income)) : "–"}
        />
        <Card
          title="Letzter Monat – Ausgaben"
          value={lastMonth ? fmtEUR(parseFloat(lastMonth.expense)) : "–"}
        />
      </div>

      <section className="bg-white dark:bg-slate-900 rounded-xl p-4 shadow-sm border border-slate-200 dark:border-slate-800">
        <h2 className="font-semibold mb-2">Cashflow pro Monat</h2>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip formatter={(v: number) => fmtEUR(v)} />
              <Legend />
              <Bar dataKey="Einnahmen" fill="#10b981" />
              <Bar dataKey="Ausgaben" fill="#ef4444" />
              <Bar dataKey="Netto" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="bg-white dark:bg-slate-900 rounded-xl p-4 shadow-sm border border-slate-200 dark:border-slate-800">
        <h2 className="font-semibold mb-2">Top-Ausgabenkategorien</h2>
        <table className="w-full text-sm">
          <thead className="text-left text-slate-500">
            <tr>
              <th className="py-1">Kategorie</th>
              <th className="py-1 text-right">Buchungen</th>
              <th className="py-1 text-right">Summe</th>
            </tr>
          </thead>
          <tbody>
            {breakdown?.slice(0, 10).map((b) => (
              <tr key={`${b.category_id ?? "none"}`} className="border-t border-slate-100 dark:border-slate-800">
                <td className="py-1.5">{b.category_name}</td>
                <td className="py-1.5 text-right">{b.transactions}</td>
                <td className="py-1.5 text-right font-mono">{fmtEUR(parseFloat(b.amount))}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function Card({ title, value }: { title: string; value: string }) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl p-4 shadow-sm border border-slate-200 dark:border-slate-800">
      <div className="text-xs uppercase text-slate-500">{title}</div>
      <div className="text-2xl font-semibold mt-1 font-mono">{value}</div>
    </div>
  );
}
