"""Turns a failed rule's evaluation trace into a plain-English explanation.

Deterministic: same trade + same rule always gives the same sentence.
"""
from __future__ import annotations

from app.schemas.internal import Trace
from app.services.rules.json_logic_evaluator import fmt

_PHRASES = {
    ">": "greater than",
    ">=": "greater than or equal to",
    "<": "less than",
    "<=": "less than or equal to",
}


def explain_failure(trace: Trace) -> str:
    findings: list[str] = []
    _collect(trace, "", findings)
    unique = list(dict.fromkeys(findings))  # drop duplicates, keep order
    return " ".join(unique) or f"Rule logic evaluated to {fmt(trace.value)}."


def _collect(t: Trace, prefix: str, out: list[str]) -> None:
    if t.truthy:
        return
    if t.op == "and":
        for child in t.children:
            _collect(child, prefix, out)
    elif t.op == "or":
        inner: list[str] = []
        for child in t.children:
            _collect(child, "", inner)
        out.append(f"{prefix}None of the alternatives hold: {' '.join(inner)}")
    elif t.op == "if" and t.detail.get("branch") in ("then", "else") and len(t.children) >= 2:
        context = _context(t.children[-2])
        _collect(t.children[-1], f"{prefix}Since {context}, ", out)
    else:
        out.append(prefix + _leaf(t))


def _context(cond: Trace) -> str:
    if cond.op == "==" and len(cond.children) == 2:
        left = cond.children[0]
        return f"{left.label} is {fmt(left.value)}"
    return f"{cond.label} evaluated to {fmt(cond.value)}"


def _unusable(t: Trace) -> str:
    if t.op == "var":
        return f"{t.label} is missing or empty."
    return f"{t.label} could not be worked out from the data."


def _ref(t: Trace) -> str:
    return fmt(t.value) if t.op == "literal" else f"{t.label} ({fmt(t.value)})"


def _leaf(t: Trace) -> str:
    op, ch = t.op, t.children

    if op == "var":
        if t.value in (None, ""):
            return f"{t.label} is missing or empty."
        return f"{t.label} has no usable value ({fmt(t.value)})."

    if op == "regex":
        field = t.detail.get("field") or (ch[0].label if ch else "value")
        subject = t.detail.get("subject")
        if subject in (None, ""):
            return f"{field} is missing or empty."
        return f"{field} ({fmt(subject)}) does not match the required pattern {t.detail['pattern']}."

    if op in ("==", "!=", ">", ">=", "<", "<=") and len(ch) == 2:
        left, right = ch
        if left.value in (None, ""):
            return _unusable(left)
        if right.value is None:
            return _unusable(right)
        if op == "==":
            return f"{left.label} is {fmt(left.value)} but must be {fmt(right.value)}."
        if op == "!=":
            return f"{left.label} is {fmt(left.value)} but must not be {fmt(right.value)}."
        return f"{left.label} ({fmt(left.value)}) must be {_PHRASES[op]} {_ref(right)}."

    if op == "in" and len(ch) == 2:
        left, right = ch
        if left.value in (None, ""):
            return _unusable(left)
        allowed = ", ".join(str(x) for x in right.value) if isinstance(right.value, list) else fmt(right.value)
        return f"{left.label} ({fmt(left.value)}) is not one of the allowed values: {allowed}."

    return f"Condition {t.label} evaluated to {fmt(t.value)}."