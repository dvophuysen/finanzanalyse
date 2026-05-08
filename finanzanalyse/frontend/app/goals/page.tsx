"use client";

import useSWR from "swr";
import { api, fetcher, fmtEUR } from "@/lib/api";
import { useState } from "react";

type Goal = {
  id: number;
  name: string;
  target_amount: string;
  saved_amount: string;
  target_date: string | null;
  priority: number;
};

export default function GoalsPage() {
  const { data: goals, mutate } = useSWR<Goal[]>("/goals", fetcher);
  const [name, setName] = useState("");
  const [target, setTarget] = useState("");
  const [date, setDate] = useState("");

  async function add() {
    if (!name || !target) return;
    await fetch(api(`/goals`), {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        name,
        target_amount: target,
        target_date: date || null,
      }),
    });
    setName("");
    setTarget("");
    setDate("");
    mutate();
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Ziele</h1>
      <section className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-200 dark:border-slate-800 space-y-3">
        <h2 className="font-semibold">Neues Ziel</h2>
        <div className="flex gap-2 flex-wrap">
          <input
            placeholder="Bezeichnung (z.B. Urlaub Italien)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="border border-slate-300 dark:border-slate-700 rounded px-2 py-1 bg-transparent"
          />
          <input
            placeholder="Zielbetrag €"
            type="number"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            className="border border-slate-300 dark:border-slate-700 rounded px-2 py-1 bg-transparent w-32"
          />
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="border border-slate-300 dark:border-slate-700 rounded px-2 py-1 bg-transparent"
          />
          <button onClick={add} className="bg-sky-600 text-white rounded px-3 py-1 text-sm">
            Hinzufügen
          </button>
        </div>
      </section>

      <section className="grid sm:grid-cols-2 gap-4">
        {goals?.map((g) => {
          const tgt = parseFloat(g.target_amount);
          const saved = parseFloat(g.saved_amount);
          const pct = tgt > 0 ? Math.min(100, (saved / tgt) * 100) : 0;
          return (
            <div
              key={g.id}
              className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-200 dark:border-slate-800"
            >
              <div className="flex justify-between items-baseline">
                <h3 className="font-semibold">{g.name}</h3>
                <span className="text-xs text-slate-500">{g.target_date ?? "ohne Datum"}</span>
              </div>
              <div className="mt-2 text-sm">
                {fmtEUR(saved)} / {fmtEUR(tgt)}
              </div>
              <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded mt-2 overflow-hidden">
                <div className="h-full bg-emerald-500" style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
        {goals && goals.length === 0 && (
          <p className="text-slate-500 text-sm">Noch keine Ziele angelegt.</p>
        )}
      </section>
    </div>
  );
}
