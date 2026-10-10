from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import Status


class RuleRef(BaseModel):
    """One rule that was checked: becomes one column of the Impact Matrix."""

    regulator_id: str
    rule_id: str
    description: str


class RuleViolation(BaseModel):
    regulator_id: str
    regulator: str
    rule_id: str
    description: str
    impact: str
    explanation: str
    evidence: dict[str, Any] = Field(default_factory=dict)  # field -> value used


class TradeResult(BaseModel):
    row_number: int  # row in the CSV file (header = row 1)
    trade_id: str  # Trade_ID from the CSV, or ROW-<n> if there is no such column
    status: Status
    trade: dict[str, str | None]  # original values, normalized column names
    regulator_status: dict[str, Status]
    violations: list[RuleViolation] = Field(default_factory=list)


class RegulatorSummary(BaseModel):
    regulator_id: str
    name: str
    rules_checked: int
    passed: int
    failed: int


class RuleFailureCount(BaseModel):
    regulator_id: str
    rule_id: str
    description: str
    failures: int


class ReportSummary(BaseModel):
    total_trades: int
    passed: int
    failed: int
    pass_rate: float
    by_regulator: list[RegulatorSummary]
    rule_failures: list[RuleFailureCount]


class ImpactReport(BaseModel):
    summary: ReportSummary
    columns: list[str]
    regulators_checked: list[str]
    rules_checked: list[RuleRef] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    results: list[TradeResult]