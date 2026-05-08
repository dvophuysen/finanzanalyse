"use client";

import useSWR from "swr";
import { fetcher, fmtEUR, api } from "@/lib/api";
import { useMemo, useState } from "react";

type Tx = {
  id: number;
  booking_date: string;
  amount: string;
  counterparty: string | null;
  purpose: string | null;
  category_id: number | null;
  category_source: string | null;
  category_confidence: string | null;
  category_reason: string | null;
  needs_review: boolean;
};

type Cat = { id: number; name: string; kind: string };

export default function TransactionsPage() {
  const [showOnlyOpen, setShowOnlyOpen] = useState(true);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [busy, setBusy] = useState<string | null>(null);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const queryKey = `/transactions?limit=500${showOnlyOpen ? "&needs_review=true" : ""}`;
  const { data: txs, mutate } = useSWR<Tx[]>(queryKey, fetcher);
  const { data: allCounts } = useSWR<Tx[]>("/transactions?limit=2000", fetcher);
  const { data: cats } = useSWR<Cat[]>("/categories", fetcher);

  const openCount = useMemo(
    () => allCounts?.filter((t) => t.needs_review).length ?? 0,
    [allCounts],
  );
  const totalCount = allCounts?.length ?? 0;

  function toggle(id: number) {
    setSelected((prev) => {
      const n = new Set(prev);
      if (n.has(id)) n.delete(id);
      else n.add(id);
      return n;
    });
  }

  function toggleAllVisible() {
    if (!txs) return;
    const visible = new Set(txs.map((t) => t.id));
    const allSelected = txs.every((t) => selected.has(t.id));
    setSelected(allSelected ? new Set() : visible);
  }

  async function setCategory(txId: number, categoryId: number) {
    await fetch(api(`/transactions/${txId}`), {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ category_id: categoryId }),
    });
    mutate();
  }

  async function confirmOne(txId: number) {
    await fetch(api("/transactions/bulk-confirm"), {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ ids: [txId] }),
    });
    mutate();
  }

  async function confirmSelected() {
    const ids = Array.from(selected);
    if (ids.length === 0) return;
    setBusy("confirm");
    try {
      const res = await fetch(api("/transactions/bulk-confirm"), {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ ids }),
      });
      const data = await res.json();
      setStatusMsg(`${data.confirmed} Buchungen bestätigt.`);
      setSelected(new Set());
      mutate();
    } finally {
      setBusy(null);
    }
  }

  async function recategorizeAll() {
    setBusy("recat");
    setStatusMsg("KI bewertet die offenen Buchungen neu – kann etwas dauern…");
    try {
      const res = await fetch(api("/transactions/recategorize-uncategorized"), { method: "POST" });
      const data = await res.json();
      setStatusMsg(
        `Fertig: ${data.categorized} Vorschläge generiert, ${data.still_uncategorized} ohne Vorschlag (von ${data.processed}).`,
      );
      mutate();
    } catch (e) {
      setStatusMsg(`Fehler: ${e}`);
    } finally {
      setBusy(null);
    }
  }

  const allVisibleSelected = txs && txs.length > 0 && txs.every((t) => selected.has(t.id));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold">Transaktionen</h1>
          <div className="text-sm text-slate-500">
            {openCount} von {totalCount} zu prüfen
          </div>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={recategorizeAll}
            disabled={busy !== null}
            className="text-sm px-3 py-1.5 rounded border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50"
          >
            {busy === "recat" ? "Läuft…" : "KI-Vorschläge neu erzeugen"}
          </button>
          <label className="text-sm flex items-center gap-2">
            <input
              type="checkbox"
              checked={showOnlyOpen}
              onChange={(e) => setShowOnlyOpen(e.target.checked)}
            />
            Nur zu prüfen
          </label>
        </div>
      </div>

      {selected.size > 0 && (
        <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-900">
          <span className="text-sm">{selected.size} ausgewählt</span>
          <button
            onClick={confirmSelected}
            disabled={busy !== null}
            className="text-sm px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            ✓ Auswahl bestätigen
          </button>
          <button
            onClick={() => setSelected(new Set())}
            className="text-sm text-slate-500 hover:text-slate-700"
          >
            Auswahl aufheben
          </button>
        </div>
      )}

      {statusMsg && (
        <div className="text-sm text-slate-600 dark:text-slate-400">{statusMsg}</div>
      )}

      <div className="overflow-x-auto bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
        <table className="w-full text-sm">
          <thead className="text-left text-slate-500 bg-slate-50 dark:bg-slate-950">
            <tr>
              <th className="px-3 py-2 w-8">
                <input
                  type="checkbox"
                  checked={!!allVisibleSelected}
                  onChange={toggleAllVisible}
                />
              </th>
              <th className="px-3 py-2">Datum</th>
              <th className="px-3 py-2">Empfänger / Zweck</th>
              <th className="px-3 py-2">Kategorie (Vorschlag)</th>
              <th className="px-3 py-2 text-right">Betrag</th>
              <th className="px-3 py-2 w-12"></th>
            </tr>
          </thead>
          <tbody>
            {txs?.length === 0 && (
              <tr>
                <td colSpan={6} className="px-3 py-8 text-center text-slate-500">
                  {showOnlyOpen ? "🎉 Alles geprüft – nichts mehr offen." : "Keine Transaktionen."}
                </td>
              </tr>
            )}
            {txs?.map((tx) => {
              const amt = parseFloat(tx.amount);
              const isOpen = tx.needs_review;
              return (
                <tr
                  key={tx.id}
                  className={`border-t border-slate-100 dark:border-slate-800 ${
                    isOpen ? "" : "opacity-60"
                  }`}
                >
                  <td className="px-3 py-2 align-top">
                    <input
                      type="checkbox"
                      checked={selected.has(tx.id)}
                      onChange={() => toggle(tx.id)}
                    />
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap align-top">{tx.booking_date}</td>
                  <td className="px-3 py-2 align-top">
                    <div className="font-medium">{tx.counterparty ?? "–"}</div>
                    <div className="text-xs text-slate-500 line-clamp-2">{tx.purpose}</div>
                  </td>
                  <td className="px-3 py-2 align-top">
                    <select
                      className="bg-transparent border border-slate-300 dark:border-slate-700 rounded px-2 py-1 text-xs w-full max-w-[260px]"
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
                    <div className="mt-1 flex items-center gap-2 text-[10px] text-slate-400">
                      {tx.category_source && (
                        <span className="uppercase">{tx.category_source}</span>
                      )}
                      {tx.category_confidence && (
                        <span>conf {parseFloat(tx.category_confidence).toFixed(2)}</span>
                      )}
                    </div>
                    {tx.category_reason && (
                      <div className="mt-0.5 text-[11px] italic text-slate-500 line-clamp-2">
                        {tx.category_reason}
                      </div>
                    )}
                  </td>
                  <td
                    className={`px-3 py-2 text-right font-mono align-top whitespace-nowrap ${
                      amt < 0 ? "text-red-600" : "text-emerald-600"
                    }`}
                  >
                    {fmtEUR(amt)}
                  </td>
                  <td className="px-3 py-2 align-top">
                    {isOpen && (
                      <button
                        onClick={() => confirmOne(tx.id)}
                        title="Bestätigen"
                        className="px-2 py-1 rounded bg-emerald-600 text-white hover:bg-emerald-700 text-xs"
                      >
                        ✓
                      </button>
                    )}
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
