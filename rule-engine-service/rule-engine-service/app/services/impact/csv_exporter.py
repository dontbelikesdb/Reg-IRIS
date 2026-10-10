"""Flattens an ImpactReport into the Impact Matrix CSV (one line per trade).

Layout:  Trade_ID | <one Pass/Fail column per selected regulator> | Violations | Impact_Explanation
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


def regulator_columns(report: ImpactReport) -> list[tuple[str, str]]:
    """(regulator_id, display name) for each selected regulator, in the order checked."""
    names = {s.regulator_id: s.name for s in report.summary.by_regulator}
    return [(rid, names.get(rid, rid)) for rid in report.regulators_checked]


def report_to_csv(report: ImpactReport, bom: bool = True) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")

    regulators = regulator_columns(report)
    writer.writerow(["Trade_ID", *(name for _, name in regulators), "Violations", "Impact_Explanation"])

    for r in report.results:
        statuses = [("Pass" if r.regulator_status.get(rid) == "PASS" else "Fail") for rid, _ in regulators]
        violations = "; ".join(v.rule_id for v in r.violations)
        explanation = " | ".join(f"[{v.rule_id}] {v.explanation}" for v in r.violations)
        writer.writerow([_safe(r.trade_id), *statuses, violations, explanation])

    return ("\ufeff" if bom else "") + buffer.getvalue()  # BOM so Excel reads UTF-8