"""Validates the uploaded CSV and turns it into trade records."""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from typing import Any

from fastapi import UploadFile

from app.schemas.internal import ServiceError

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_ROWS = 50_000

# Column names the rules rely on. "asset class", "AssetClass", "ASSET_CLASS"
# all become "Asset_Class".
KNOWN_COLUMNS = [
    "Trade_ID", "Asset_Class", "Underlying_ISIN", "Quantity", "Price",
    "Currency", "Counterparty_LEI", "Maturity_Date", "Timestamp",
]
_NUMERIC = {"Quantity", "Price"}


def _squash(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


_CANONICAL = {_squash(n): n for n in KNOWN_COLUMNS}


@dataclass
class Trade:
    row_number: int
    raw: dict[str, str | None]  # original text values (shown in the report)
    data: dict[str, Any]  # typed values (used by the rules)


@dataclass
class ParsedTrades:
    columns: list[str]
    trades: list[Trade]


async def read_upload(file: UploadFile) -> bytes:
    if not (file.filename or "").lower().endswith(".csv"):
        raise ServiceError("Please upload a .csv file.", 415)
    content = await file.read(MAX_FILE_BYTES + 1)
    if len(content) > MAX_FILE_BYTES:
        raise ServiceError(f"File is larger than {MAX_FILE_BYTES // (1024 * 1024)} MB.", 413)
    if not content.strip():
        raise ServiceError("The uploaded file is empty.", 400)
    return content


def _decode(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return content.decode("latin-1")


def _delimiter(text: str) -> str:
    lines = text.splitlines()
    header = lines[0] if lines else ""
    return max(",;\t", key=header.count) if any(d in header for d in ",;\t") else ","


def _normalize_headers(header: list[str]) -> list[str | None]:
    out: list[str | None] = []
    seen: set[str] = set()
    for h in header:
        h = h.strip()
        if not h:
            out.append(None)
            continue
        name = _CANONICAL.get(_squash(h)) or re.sub(r"\s+", "_", h)
        if name in seen:
            raise ServiceError(f"Duplicate column '{name}' after normalizing headers.", 422)
        seen.add(name)
        out.append(name)
    return out


def _typed(col: str, value: str | None) -> Any:
    if value is None or col not in _NUMERIC:
        return value
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value  # leave as text; the rule will fail it with an explanation


def parse_trades(content: bytes) -> ParsedTrades:
    text = _decode(content)
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=_delimiter(text))
    try:
        header = next(reader)
    except StopIteration:
        raise ServiceError("The CSV has no header row.", 422)

    columns = _normalize_headers(header)
    names = [c for c in columns if c]
    if not names:
        raise ServiceError("The CSV header row is empty.", 422)

    trades: list[Trade] = []
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue  # skip blank lines
        if len(trades) >= MAX_ROWS:
            raise ServiceError(f"Too many rows (limit is {MAX_ROWS:,}).", 413)
        raw: dict[str, str | None] = {c: None for c in names}
        for col, cell in zip(columns, row):
            if col:
                raw[col] = cell.strip() or None
        data = {c: _typed(c, v) for c, v in raw.items()}
        trades.append(Trade(row_number=reader.line_num, raw=raw, data=data))

    if not trades:
        raise ServiceError("The CSV has a header but no trade rows.", 422)
    return ParsedTrades(columns=names, trades=trades)