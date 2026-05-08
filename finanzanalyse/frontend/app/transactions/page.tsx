"use client";

import useSWR from "swr";
import { fetcher, fmtEUR, api } from "@/lib/api";
import { useState } from "react";

type Tx = {
  id: number;
  booking_date: string;
  amount: string;
  counterparty: string | null;
  purpose: string | null;
  category_id: number | null;
  category_source: string | null;
  category_confidence: string | null;
};

type Cat = { id: number; name: string; kind: string };

export default function TransactionsPage() {
  const [onlyUncat, setOnlyUncat] = useState(false);
  const [recatBusy, setRecatBusy] = useState(false);
  const [recatMsg, setRecatMsg] = useState<string | null>(null);
  const { data: txs, mutate } = useSWR<Tx[]>(
    `/transactions?limit=500${onlyUncat ? "&uncategorized=true" : ""}`,
    fetcher,
  );
  const { data: cats } = useSWR<Cat[]>("/categories", fetcher);

  async function setCategory(txId: number, categoryId: number) {
    await fetch(api(`/transactions/${txId}`), {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ category_id: categoryId }),
    });
    mutate();
  }

  async function recategorizeAll() {
    setRecatBusy(true);
    setRecatMsg("Laeuft – kann ein paar Minuten dauern...");
    try {
      const res = await fetch(api("/transactions/recategorize-uncategorized"), { method: "POST" });
      const data = await res.json();
      setRecatMsg(
        `Fertig: ${data.categorized} kategorisiert, ${data.still_uncategorized} weiterhin offen (von ${data.processed}).`,
      );
      mutate();
    } catch (e) {
      setRecatMsg(`Fehler: ${e}`);
    } finally {
      setRecatBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <h1 className="text-2xl font-bold">Transaktionen</h1>
        <div className="flex items-center gap-3">
          <button
            onClick={recategorizeAll}
            disabled={recatBusy}
            className="text-sm px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {recatBusy ? "Laeuft..." : "Unkategorisierte neu kategorisieren"}
          </button>
          <label className="text-sm flex items-center gap-2">
            <input
              type="checkbox"
              checked={onlyUncat}
              onChange={(e) => setOnlyUncat(e.target.checked)}
            />
            Nur offene (uncategorisiert + Sonstiges)
          </label>
        </div>
      </div>
      {recatMsg && <div className="text-sm text-slate-600 dark:text-slate-400">{recatMsg}</div>}

      <div className="overflow-x-auto bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
        <table className="w-full text-sm">
          <thead className="text-left text-slate-500">
            <tr>
              <th className="px-3 py-2">Datum</th>
              <th className="px-3 py-2">Empfänger / Zweck</th>
              <th className="px-3 py-2">Kategorie</th>
              <th className="px-3 py-2 text-right">Betrag</th>
            </tr>
          </thead>
          <tbody>
            {txs?.map((tx) => {
              const amt = parseFloat(tx.amount);
              return (
                <tr key={tx.id} className="border-t border-slate-100 dark:border-slate-800">
                  <td className="px-3 py-2 whitespace-nowrap">{tx.booking_date}</td>
                  <td className="px-3 py-2">
                    <div className="font-medium">{tx.counterparty ?? "–"}</div>
                    <div className="text-xs text-slate-500 line-clamp-1">{tx.purpose}</div>
                  </td>
                  <td className="px-3 py-2">
                    <select
                      className="bg-transparent border border-slate-300 dark:border-slate-700 rounded px-2 py-1 text-xs"
                      value={tx.category_id ?? ""}
                      onChange={(e) => setCategory(tx.id, parseInt(e.target.value))}
                    >
                      <option value="" disabled>
                        — wählen —
                      </option>
                      {cats?.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name}
                        </option>
                      ))}
                    </select>
                    {tx.category_source && (
                      <span className="ml-2 text-[10px] uppercase text-slate-400">
                        {tx.category_source}
                      </span>
                    )}
                  </td>
                  <td
                    className={`px-3 py-2 text-right font-mono ${
                      amt < 0 ? "text-red-600" : "text-emerald-600"
                    }`}
                  >
                    {fmtEUR(amt)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
