"""Flattens an ImpactReport into a CSV (one line per trade)."""
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

    reg_cols = [f"{rid}_Status" for rid in report.regulators_checked]
    writer.writerow(["Row", *report.columns, "Overall_Status", *reg_cols, "Failed_Rules", "Violation_Details"])

    for r in report.results:
        failed_rules = "; ".join(f"{v.regulator_id}:{v.rule_id}" for v in r.violations)
        details = " | ".join(f"[{v.rule_id}] {v.explanation}" for v in r.violations)
        writer.writerow([
            r.row_number,
            *(_safe(r.trade.get(c)) for c in report.columns),
            r.status,
            *(r.regulator_status.get(rid, "") for rid in report.regulators_checked),
            failed_rules,
            details,
        ])

    return ("\ufeff" if bom else "") + buffer.getvalue()  # BOM so Excel reads UTF-8