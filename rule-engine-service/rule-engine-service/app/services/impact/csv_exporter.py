"""Flattens an ImpactReport into the Impact Matrix CSV (one line per trade).

Layout:  Trade_ID | Row | <one Pass/Fail column per rule> | Overall_Status |
         Failed_Rules | Violation_Details | <the rest of the original trade fields>
"""
from __future__ import annotations

import csv
import io

from app.schemas.impact import ImpactReport

_FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r")


def _is_number(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def _safe(value: str | None) -> str:
    """Stops Excel from running a cell like =HYPERLINK(...) as a formula."""
    if value is None:
        return ""
    if value.startswith(_FORMULA_STARTS) and not _is_number(value):
        return "'" + value
    return value


def report_to_csv(report: ImpactReport, bom: bool = True) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")  # csv module handles quoting/escaping

    rules = report.rules_checked
    other_columns = [c for c in report.columns if c != "Trade_ID"]
    writer.writerow([
        "Trade_ID", "Row", *(r.rule_id for r in rules),
        "Overall_Status", "Failed_Rules", "Violation_Details", *other_columns,
    ])

    for r in report.results:
        failed = {(v.regulator_id, v.rule_id) for v in r.violations}
        cells = ["Fail" if (rr.regulator_id, rr.rule_id) in failed else "Pass" for rr in rules]
        failed_rules = "; ".join(f"{v.regulator_id}:{v.rule_id}" for v in r.violations)
        details = " | ".join(f"[{v.rule_id}] {v.explanation}" for v in r.violations)
        writer.writerow([
            _safe(r.trade_id),
            r.row_number,
            *cells,
            r.status,
            failed_rules,
            details,
            *(_safe(r.trade.get(c)) for c in other_columns),
        ])

    return ("\ufeff" if bom else "") + buffer.getvalue()  # BOM so Excel reads UTF-8