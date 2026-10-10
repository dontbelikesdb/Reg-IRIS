"""Finds, reads and validates regulator rule files.

Drop a new file called rules_<id>.json into the rules folder and it shows up
as a regulator automatically (id = the part after "rules_", upper-cased).
Users can also upload a rules_<id>.json at request time (see parse_uploaded_ruleset).
"""
from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path

from app.schemas.internal import Rule, RuleSet, ServiceError
from app.services.rules.json_logic_evaluator import validate_logic, validate_regexes

logger = logging.getLogger(__name__)

# app/services/rules/rule_loader.py -> app/data/rules  (override with RULES_DIR)
RULES_DIR = Path(os.getenv("RULES_DIR", Path(__file__).resolve().parents[2] / "data"))
_PREFIX = "rules_"
_REQUIRED_RULE_KEYS = ("id", "description", "logic", "impact")

# Limits for rule files uploaded by users
MAX_RULE_FILE_BYTES = 1024 * 1024
MAX_RULES_PER_FILE = 500
MAX_CUSTOM_FILES = 10
_UPLOAD_NAME = re.compile(r"^rules_([A-Za-z0-9][A-Za-z0-9_-]{0,39})\.json$", re.IGNORECASE)


def _regulator_id(path: Path) -> str:
    return path.stem[len(_PREFIX):].upper()


def _rule_files() -> dict[str, Path]:
    if not RULES_DIR.is_dir():
        return {}
    return {_regulator_id(p): p for p in sorted(RULES_DIR.glob(f"{_PREFIX}*.json"))}


def _build_ruleset(raw: object, source: str, rid: str, *, status: int = 500, strict: bool = False) -> RuleSet:
    """Validate parsed JSON and turn it into a RuleSet.

    `source` is only used in error messages. `status` is the HTTP status for a bad
    file (500 for our own files, 422 for uploads). `strict` adds the extra checks
    meant for untrusted, user-uploaded files.
    """

    def fail(message: str, cause: Exception | None = None) -> ServiceError:
        err = ServiceError(f"{source}: {message}", status)
        err.__cause__ = cause
        return err

    if not isinstance(raw, dict) or not isinstance(raw.get("rules"), list):
        raise fail("expected an object with a 'rules' list")
    if strict and not raw["rules"]:
        raise fail("the 'rules' list is empty")
    if strict and len(raw["rules"]) > MAX_RULES_PER_FILE:
        raise fail(f"too many rules (limit is {MAX_RULES_PER_FILE})")

    rules: list[Rule] = []
    seen: set[str] = set()
    for i, item in enumerate(raw["rules"]):
        if not isinstance(item, dict):
            raise fail(f"rule #{i + 1} is not an object")
        missing = [k for k in _REQUIRED_RULE_KEYS if k not in item]
        if missing:
            raise fail(f"rule #{i + 1} is missing {', '.join(missing)}")
        for key in ("id", "description", "impact"):
            if not isinstance(item[key], str) or not item[key].strip():
                raise fail(f"rule #{i + 1}: '{key}' must be a non-empty text value")
        if item["id"] in seen:
            raise fail(f"duplicate rule id {item['id']}")
        seen.add(item["id"])
        try:
            validate_logic(item["logic"])
            if strict:
                validate_regexes(item["logic"])
        except ValueError as exc:
            raise fail(f"{item['id']}: {exc}", exc) from exc
        rules.append(Rule(item["id"], item["description"], item["impact"], item["logic"]))

    name, jurisdiction = raw.get("regulator", rid), raw.get("jurisdiction", "")
    if not isinstance(name, str) or not isinstance(jurisdiction, str):
        raise fail("'regulator' and 'jurisdiction' must be text")
    return RuleSet(id=rid, name=name.strip() or rid, jurisdiction=jurisdiction.strip(), rules=tuple(rules))


def _parse_file(path: Path) -> RuleSet:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ServiceError(f"Could not read rule file {path.name}: {exc}", 500) from exc
    return _build_ruleset(raw, path.name, _regulator_id(path))


def parse_uploaded_ruleset(filename: str | None, content: bytes) -> RuleSet:
    """Validate a regulator rule file uploaded by a user. Nothing is stored.

    The file must be called rules_<regulatorName>.json; the regulator id is the
    name part, upper-cased (rules_emir.json -> EMIR), exactly like the built-in files.
    """
    name = Path(filename or "").name
    match = _UPLOAD_NAME.match(name)
    if not match:
        raise ServiceError(
            f"'{name or 'file'}' must be named rules_<regulatorName>.json "
            "(letters, digits, '_' or '-'), for example rules_emir.json.",
            422,
        )
    rid = match.group(1).upper()
    if rid in _rule_files():
        raise ServiceError(
            f"{name}: a built-in regulator with id {rid} already exists. "
            f"Rename the file, e.g. rules_{rid.lower()}_custom.json.",
            409,
        )
    if len(content) > MAX_RULE_FILE_BYTES:
        raise ServiceError(f"{name}: file is larger than {MAX_RULE_FILE_BYTES // 1024} KB.", 413)
    try:
        raw = json.loads(content.decode("utf-8-sig"))
    except UnicodeDecodeError as exc:
        raise ServiceError(f"{name}: file must be UTF-8 encoded JSON.", 422) from exc
    except ValueError as exc:
        raise ServiceError(f"{name}: not valid JSON ({exc}).", 422) from exc
    return _build_ruleset(raw, name, rid, status=422, strict=True)


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


def resolve_rulesets(ids: list[str], custom: list[RuleSet] | tuple[RuleSet, ...] = ()) -> list[RuleSet]:
    """Built-in regulators picked by id plus any uploaded rule sets, ready to evaluate."""
    selected = load_regulators(ids) if ids else []
    seen = {rs.id for rs in selected}
    for rs in custom:
        if rs.id in seen:
            raise ServiceError(f"Regulator '{rs.id}' was supplied more than once.", 422)
        seen.add(rs.id)
        selected.append(rs)
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