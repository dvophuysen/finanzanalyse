"use client";

import { useState } from "react";
import useSWR from "swr";
import { api, fetcher } from "@/lib/api";

type Account = { id: number; name: string; bank_name: string | null };

export default function ImportPage() {
  const { data: accounts, mutate } = useSWR<Account[]>("/accounts", fetcher);
  const [file, setFile] = useState<File | null>(null);
  const [accountId, setAccountId] = useState<number | "">("");
  const [useLLM, setUseLLM] = useState(true);
  const [result, setResult] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Konto-Anlage
  const [newName, setNewName] = useState("");
  const [newBank, setNewBank] = useState("");

  async function createAccount() {
    if (!newName) return;
    await fetch(api(`/accounts`), {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ name: newName, bank_name: newBank || null }),
    });
    setNewName("");
    setNewBank("");
    mutate();
  }

  async function upload() {
    if (!file || !accountId) return;
    setBusy(true);
    setResult(null);
    const fd = new FormData();
    fd.append("account_id", String(accountId));
    fd.append("file", file);
    fd.append("use_llm", String(useLLM));
    const res = await fetch(api(`/import/csv`), { method: "POST", body: fd });
    const data = await res.json();
    setBusy(false);
    if (!res.ok) {
      setResult(`Fehler: ${data.detail ?? res.statusText}`);
    } else {
      setResult(
        `Importiert: ${data.imported}, Duplikate: ${data.duplicates}, übersprungen: ${data.skipped}`,
      );
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Import</h1>

      <section className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-200 dark:border-slate-800 space-y-3">
        <h2 className="font-semibold">Neues Konto anlegen</h2>
        <div className="flex gap-2 flex-wrap">
          <input
            placeholder="Bezeichnung (z.B. ING Giro)"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="border border-slate-300 dark:border-slate-700 rounded px-2 py-1 bg-transparent"
          />
          <input
            placeholder="Bank"
            value={newBank}
            onChange={(e) => setNewBank(e.target.value)}
            className="border border-slate-300 dark:border-slate-700 rounded px-2 py-1 bg-transparent"
          />
          <button
            onClick={createAccount}
            className="bg-sky-600 text-white rounded px-3 py-1 text-sm"
          >
            Anlegen
          </button>
        </div>
      </section>

      <section className="bg-white dark:bg-slate-900 rounded-xl p-4 border border-slate-200 dark:border-slate-800 space-y-3">
        <h2 className="font-semibold">CSV importieren</h2>
        <div className="flex gap-2 flex-wrap items-center">
          <select
            value={accountId}
            onChange={(e) => setAccountId(e.target.value ? Number(e.target.value) : "")}
            className="border border-slate-300 dark:border-slate-700 rounded px-2 py-1 bg-transparent"
          >
            <option value="" disabled>
              — Konto wählen —
            </option>
            {accounts?.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name} {a.bank_name ? `(${a.bank_name})` : ""}
              </option>
            ))}
          </select>
          <input
            type="file"
            accept=".csv,text/csv"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <label className="text-sm flex items-center gap-1">
            <input
              type="checkbox"
              checked={useLLM}
              onChange={(e) => setUseLLM(e.target.checked)}
            />
            KI-Kategorisierung
          </label>
          <button
            disabled={!file || !accountId || busy}
            onClick={upload}
            className="bg-emerald-600 text-white rounded px-3 py-1 text-sm disabled:opacity-50"
          >
            {busy ? "Importiere…" : "Hochladen"}
          </button>
        </div>
        {result && <div className="text-sm">{result}</div>}
        <p className="text-xs text-slate-500">
          Unterstützt CSV-Exporte von DKB, ING, Sparkasse, Comdirect und generische
          Formate. Spalten werden automatisch erkannt.
        </p>
      </section>
    </div>
  );
}
