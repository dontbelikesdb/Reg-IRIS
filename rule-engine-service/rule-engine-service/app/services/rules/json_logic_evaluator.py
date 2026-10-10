"""A small recursive JSON Logic interpreter that records a trace of what it did.

Supported: and, or, if, !, !!, ==, !=, >, >=, <, <=, in, regex, substr, toNumber, var
"""
from __future__ import annotations

import math
import re
from functools import lru_cache
from typing import Any

from app.schemas.internal import Trace

SUPPORTED_OPERATORS = {
    "and", "or", "if", "!", "!!", "==", "!=", ">", ">=", "<", "<=",
    "in", "regex", "substr", "toNumber", "var",
}


class EvaluationError(Exception):
    pass


# ---------- helpers -------------------------------------------------------

def fmt(value: Any) -> str:
    """Readable form of a value for explanations."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f"'{value}'"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, list):
        return "[" + ", ".join(fmt(v) for v in value) + "]"
    return str(value)


def _num(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v) if math.isfinite(v) else None
    if isinstance(v, str):
        try:
            n = float(v.strip())
        except ValueError:
            return None
        return n if math.isfinite(n) else None
    return None


def _to_number(v: Any) -> int | float | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        s = v.strip()
        # ISO dates (2018-01-01) become 20180101 so date rules can compare them
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
            return int(s.replace("-", ""))
        try:
            return int(s)
        except ValueError:
            pass
        return _num(s)
    return None


def _loose_eq(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, str) and isinstance(b, str):
        return a == b
    na, nb = _num(a), _num(b)
    if na is not None and nb is not None:
        return na == nb
    return a == b


def _compare(op: str, a: Any, b: Any) -> bool:
    if a is None or b is None:
        return False
    na, nb = _num(a), _num(b)
    if na is not None and nb is not None:
        x, y = na, nb
    elif isinstance(a, str) and isinstance(b, str):
        x, y = a, b
    else:
        return False
    return {">": x > y, ">=": x >= y, "<": x < y, "<=": x <= y}[op]


@lru_cache(maxsize=256)
def _compile(pattern: str) -> re.Pattern:
    try:
        return re.compile(pattern)
    except re.error as exc:
        raise EvaluationError(f"Invalid regex '{pattern}': {exc}") from exc


def _lookup(data: dict[str, Any], name: str) -> Any:
    if name in data:
        return data[name]
    cur: Any = data
    for part in name.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def _label(op: str, children: list[Trace]) -> str:
    return f"{op}({', '.join(c.label for c in children)})"


# ---------- static checks (used by the rule loader) -----------------------

def validate_logic(logic: Any, path: str = "logic") -> None:
    """Raise ValueError if the logic uses an unsupported operator or bad shape."""
    if isinstance(logic, list):
        for i, item in enumerate(logic):
            validate_logic(item, f"{path}[{i}]")
        return
    if not isinstance(logic, dict):
        return
    if len(logic) != 1:
        raise ValueError(f"{path}: an operator object must have exactly one key")
    op, args = next(iter(logic.items()))
    if op not in SUPPORTED_OPERATORS:
        raise ValueError(f"{path}: unsupported operator '{op}'")
    if op != "var":
        validate_logic(args, f"{path}.{op}")


def extract_fields(logic: Any) -> set[str]:
    """Every data field a piece of logic reads."""
    out: set[str] = set()
    if isinstance(logic, list):
        for item in logic:
            out |= extract_fields(item)
    elif isinstance(logic, dict):
        for op, raw in logic.items():
            args = raw if isinstance(raw, list) else [raw]
            if op == "var":
                if args and isinstance(args[0], str) and args[0]:
                    out.add(args[0])
                continue
            if op == "regex" and args and isinstance(args[0], str):
                out.add(args[0])  # regex takes a bare field name as 1st arg
                args = args[1:]
            for a in args:
                out |= extract_fields(a)
    return out


def collect_fields(trace: Trace) -> dict[str, Any]:
    """Field -> value pairs that a rule actually looked at (the 'evidence')."""
    out: dict[str, Any] = {}

    def walk(t: Trace) -> None:
        if t.op == "var":
            out[t.detail["field"]] = t.value
        elif t.op == "regex" and t.detail.get("field"):
            out[t.detail["field"]] = t.detail["subject"]
        for c in t.children:
            walk(c)

    walk(trace)
    return out


# ---------- evaluator ------------------------------------------------------

def evaluate(logic: Any, data: dict[str, Any]) -> Trace:
    if isinstance(logic, list):
        children = [evaluate(i, data) for i in logic]
        values = [c.value for c in children]
        return Trace("list", values, fmt(values), children)

    if not isinstance(logic, dict):
        return Trace("literal", logic, fmt(logic))

    if len(logic) != 1:
        raise EvaluationError("An operator object must have exactly one key")
    op, raw = next(iter(logic.items()))
    if op not in SUPPORTED_OPERATORS:
        raise EvaluationError(f"Unsupported operator '{op}'")
    args = raw if isinstance(raw, list) else [raw]

    if op == "var":
        name = args[0] if args else ""
        default = args[1] if len(args) > 1 else None
        name = name if isinstance(name, str) else str(name)
        value = _lookup(data, name)
        if value is None:
            value = default
        return Trace("var", value, name, detail={"field": name})

    if op in ("and", "or"):
        # Every branch is evaluated (no short-circuit) so explanations can list
        # *all* failing conditions. The result is the same as normal JSON Logic.
        children = [evaluate(a, data) for a in args]
        if op == "and":
            hit = next((c for c in children if not c.truthy), None)
        else:
            hit = next((c for c in children if c.truthy), None)
        if hit is not None:
            value = hit.value
        else:
            value = children[-1].value if children else (op == "and")
        return Trace(op, value, _label(op, children), children)

    if op == "if":
        children = []
        i = 0
        while i + 1 < len(args):
            cond = evaluate(args[i], data)
            children.append(cond)
            if cond.truthy:
                branch = evaluate(args[i + 1], data)
                children.append(branch)
                return Trace("if", branch.value, _label("if", children), children, {"branch": "then"})
            i += 2
        if i < len(args):
            branch = evaluate(args[i], data)
            children.append(branch)
            return Trace("if", branch.value, _label("if", children), children, {"branch": "else"})
        return Trace("if", None, _label("if", children), children, {"branch": "none"})

    # ---- eager operators ----
    children = [evaluate(a, data) for a in args]
    vals = [c.value for c in children]
    a = vals[0] if vals else None
    b = vals[1] if len(vals) > 1 else None
    detail: dict[str, Any] = {}
    label = _label(op, children)

    if op == "==":
        value: Any = _loose_eq(a, b)
    elif op == "!=":
        value = not _loose_eq(a, b)
    elif op in (">", ">=", "<", "<="):
        value = _compare(op, a, b)
    elif op == "in":
        if isinstance(b, list):
            value = any(_loose_eq(a, x) for x in b)
        elif isinstance(b, str) and a is not None:
            value = str(a) in b
        else:
            value = False
    elif op == "regex":
        if len(args) != 2 or not isinstance(b, str):
            raise EvaluationError("regex needs [field_or_value, pattern]")
        if isinstance(args[0], str):  # bare field name, as used in the rule files
            field_name: str | None = args[0]
            subject = _lookup(data, args[0])
        else:
            field_name = None
            subject = a
        compiled = _compile(b)
        value = subject not in (None, "") and compiled.search(str(subject)) is not None
        detail = {"field": field_name, "subject": subject, "pattern": b}
        label = f"regex({field_name or children[0].label}, {fmt(b)})"
    elif op == "substr":
        if a is None:
            value = None
        else:
            s = str(a)
            start = int(_num(b) or 0)
            if start < 0:
                start = max(len(s) + start, 0)
            length = _num(vals[2]) if len(vals) > 2 else None
            if length is None:
                end = len(s)
            elif length >= 0:
                end = start + int(length)
            else:
                end = len(s) + int(length)
            value = s[start:end]
    elif op == "toNumber":
        value = _to_number(a)
    elif op == "!":
        value = not bool(a)
    else:  # "!!"
        value = bool(a)

    return Trace(op, value, label, children, detail)