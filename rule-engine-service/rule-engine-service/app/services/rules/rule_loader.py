"""Finds, reads and validates regulator rule files.

Drop a new file called rules_<id>.json into the rules folder and it shows up
as a regulator automatically (id = the part after "rules_", upper-cased).
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from app.schemas.internal import Rule, RuleSet, ServiceError
from app.services.rules.json_logic_evaluator import validate_logic

logger = logging.getLogger(__name__)

# app/services/rules/rule_loader.py -> app/data/rules  (override with RULES_DIR)
RULES_DIR = Path(os.getenv("RULES_DIR", Path(__file__).resolve().parents[2] / "data"))
_PREFIX = "rules_"
_REQUIRED_RULE_KEYS = ("id", "description", "logic", "impact")


def _regulator_id(path: Path) -> str:
    return path.stem[len(_PREFIX):].upper()


def _rule_files() -> dict[str, Path]:
    if not RULES_DIR.is_dir():
        return {}
    return {_regulator_id(p): p for p in sorted(RULES_DIR.glob(f"{_PREFIX}*.json"))}


def _parse_file(path: Path) -> RuleSet:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ServiceError(f"Could not read rule file {path.name}: {exc}", 500) from exc

    if not isinstance(raw, dict) or not isinstance(raw.get("rules"), list):
        raise ServiceError(f"{path.name}: expected an object with a 'rules' list", 500)

    rules: list[Rule] = []
    seen: set[str] = set()
    for i, item in enumerate(raw["rules"]):
        if not isinstance(item, dict):
            raise ServiceError(f"{path.name}: rule #{i + 1} is not an object", 500)
        missing = [k for k in _REQUIRED_RULE_KEYS if k not in item]
        if missing:
            raise ServiceError(f"{path.name}: rule #{i + 1} is missing {', '.join(missing)}", 500)
        if item["id"] in seen:
            raise ServiceError(f"{path.name}: duplicate rule id {item['id']}", 500)
        seen.add(item["id"])
        try:
            validate_logic(item["logic"])
        except ValueError as exc:
            raise ServiceError(f"{path.name} / {item['id']}: {exc}", 500) from exc
        rules.append(Rule(item["id"], item["description"], item["impact"], item["logic"]))

    rid = _regulator_id(path)
    return RuleSet(
        id=rid,
        name=raw.get("regulator", rid),
        jurisdiction=raw.get("jurisdiction", ""),
        rules=tuple(rules),
    )


def list_regulators() -> list[RuleSet]:
    """All valid regulators (a broken file is logged and skipped)."""
    out = []
    for path in _rule_files().values():
        try:
            out.append(_parse_file(path))
        except ServiceError as exc:
            logger.warning("Skipping rule file: %s", exc.message)
    return out


def load_regulators(ids: list[str]) -> list[RuleSet]:
    """Load the selected regulators; unknown ids raise a 422."""
    available = _rule_files()
    selected: list[RuleSet] = []
    done: set[str] = set()
    for raw_id in ids:
        rid = raw_id.strip().upper()
        if rid in done:
            continue
        if rid not in available:
            options = ", ".join(available) or "none found"
            raise ServiceError(f"Unknown regulator '{raw_id}'. Available: {options}", 422)
        selected.append(_parse_file(available[rid]))
        done.add(rid)
    if not selected:
        raise ServiceError("Select at least one regulator.", 422)
    return selected

def validate_all() -> list[dict]:
    """Health check: try to load every rules_*.json and report what happened."""
    report = []
    for rid, path in _rule_files().items():
        try:
            rs = _parse_file(path)
            report.append({"file": path.name, "regulator_id": rid, "ok": True,
                           "rule_count": len(rs.rules), "error": None})
        except ServiceError as exc:
            report.append({"file": path.name, "regulator_id": rid, "ok": False,
                           "rule_count": 0, "error": exc.message})
    return report