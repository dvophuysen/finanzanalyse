"""CSV-Import für deutsche Banken (DKB, ING, Sparkasse, Comdirect, generisch)."""

from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

import chardet
import pandas as pd

GERMAN_DATE_FORMATS = ("%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d")


@dataclass
class ParsedTx:
    booking_date: datetime
    value_date: datetime | None
    amount: Decimal
    counterparty: str | None
    purpose: str | None
    raw_text: str
    external_id: str


def _decode(raw: bytes) -> str:
    enc = chardet.detect(raw).get("encoding") or "utf-8"
    return raw.decode(enc, errors="replace")


def _parse_amount(s: str) -> Decimal:
    if s is None:
        raise ValueError("leerer Betrag")
    s = str(s).strip().replace("\xa0", " ").replace(" ", "").replace("EUR", "").replace("€", "")
    if not s:
        raise ValueError("leerer Betrag")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return Decimal(s)
    except InvalidOperation as e:
        raise ValueError(f"Betrag nicht parsbar: {s}") from e


def _parse_date(s: str) -> datetime:
    s = str(s).strip()
    for fmt in GERMAN_DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Datum nicht parsbar: {s}")


# Spalten-Heuristiken: untere-Case-Substring -> Feld
COLUMN_HINTS = {
    "booking_date": ["buchung", "buchungstag", "valuta-buchung", "datum"],
    "value_date": ["wertstellung", "valuta"],
    "counterparty": [
        "auftraggeber",
        "empfänger",
        "empfaenger",
        "beguenstigter",
        "begünstigter",
        "name",
    ],
    "purpose": ["verwendungszweck", "buchungstext", "beschreibung", "zweck"],
    "amount": ["betrag", "umsatz"],
}


def _resolve_columns(cols: list[str]) -> dict[str, str]:
    lc = {c: c.lower() for c in cols}
    resolved: dict[str, str] = {}
    for field, hints in COLUMN_HINTS.items():
        for col, low in lc.items():
            if any(h in low for h in hints):
                resolved.setdefault(field, col)
                break
    return resolved


def parse_csv(content: bytes) -> list[ParsedTx]:
    text = _decode(content)
    # Banken-Header haben oft Vorspann; finde die Header-Zeile
    lines = text.splitlines()
    header_idx = 0
    for i, line in enumerate(lines):
        low = line.lower()
        if ("buchung" in low or "datum" in low) and ("betrag" in low or "umsatz" in low):
            header_idx = i
            break

    csv_text = "\n".join(lines[header_idx:])

    for sep in (";", ",", "\t"):
        try:
            df = pd.read_csv(io.StringIO(csv_text), sep=sep, dtype=str, engine="python")
            if len(df.columns) >= 3:
                break
        except Exception:
            continue
    else:
        raise ValueError("CSV konnte nicht gelesen werden")

    df.columns = [c.strip() for c in df.columns]
    cols = _resolve_columns(list(df.columns))
    if "booking_date" not in cols or "amount" not in cols:
        raise ValueError(
            f"Pflichtspalten fehlen. Gefunden: {list(df.columns)}, Mapping: {cols}"
        )

    out: list[ParsedTx] = []
    for _, row in df.iterrows():
        try:
            booking = _parse_date(row[cols["booking_date"]])
        except (ValueError, KeyError):
            continue
        try:
            amount = _parse_amount(row[cols["amount"]])
        except ValueError:
            continue

        value = None
        if "value_date" in cols and pd.notna(row.get(cols["value_date"])):
            try:
                value = _parse_date(row[cols["value_date"]])
            except ValueError:
                value = None

        counterparty = (
            str(row[cols["counterparty"]]).strip() if "counterparty" in cols and pd.notna(row.get(cols["counterparty"])) else None
        )
        purpose = (
            str(row[cols["purpose"]]).strip() if "purpose" in cols and pd.notna(row.get(cols["purpose"])) else None
        )

        raw = " | ".join(f"{c}={row[c]}" for c in df.columns if pd.notna(row.get(c)))
        ext_id = hashlib.sha1(
            f"{booking.date()}|{amount}|{counterparty}|{purpose}|{raw}".encode()
        ).hexdigest()[:24]

        out.append(
            ParsedTx(
                booking_date=booking,
                value_date=value,
                amount=amount,
                counterparty=counterparty or None,
                purpose=purpose or None,
                raw_text=raw,
                external_id=ext_id,
            )
        )
    return out
