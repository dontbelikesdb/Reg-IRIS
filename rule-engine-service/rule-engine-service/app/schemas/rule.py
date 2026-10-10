from typing import Any

from pydantic import BaseModel


class RuleInfo(BaseModel):
    id: str
    description: str
    impact: str


class RegulatorInfo(BaseModel):
    id: str
    name: str
    jurisdiction: str
    rule_count: int
    rules: list[RuleInfo]


class RegulatorListResponse(BaseModel):
    regulators: list[RegulatorInfo]


# ---- used by api/internal.py ----
class RuleFileStatus(BaseModel):
    file: str
    regulator_id: str
    ok: bool
    rule_count: int
    error: str | None = None


class RuleTestRequest(BaseModel):
    logic: Any  # one rule's JSON Logic
    trade: dict[str, Any]  # one trade, already typed (numbers as numbers)


class RuleTestResult(BaseModel):
    passed: bool
    explanation: str | None = None
    evidence: dict[str, Any] = {}