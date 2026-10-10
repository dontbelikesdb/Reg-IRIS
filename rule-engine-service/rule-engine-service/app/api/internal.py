"""Developer / debugging tools. Not meant for the React UI.

Keep these off (or behind auth) in production.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.internal import ServiceError
from app.schemas.rule import RuleFileStatus, RuleTestRequest, RuleTestResult
from app.services.rules.explanation_builder import explain_failure
from app.services.rules.json_logic_evaluator import (
    EvaluationError, collect_fields, evaluate, validate_logic,
)
from app.services.rules.rule_loader import load_regulators, validate_all

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/rules/status", response_model=list[RuleFileStatus])
def rule_file_status():
    """Is every rules_*.json loadable? Shows the exact error for broken ones."""
    return validate_all()


@router.get("/rules/{regulator_id}/logic")
def raw_rule_logic(regulator_id: str):
    """The raw JSON Logic of every rule in a regulator, as the engine sees it."""
    try:
        rs = load_regulators([regulator_id])[0]
    except ServiceError as exc:
        status = 404 if exc.status_code == 422 else exc.status_code
        raise HTTPException(status_code=status, detail=exc.message)
    return {r.id: r.logic for r in rs.rules}


@router.post("/rules/test", response_model=RuleTestResult)
def test_rule(body: RuleTestRequest):
    """Try one rule's logic against one trade, no CSV needed.

    Handy while writing or fixing a rule.
    """
    try:
        validate_logic(body.logic)
        trace = evaluate(body.logic, body.trade)
    except (ValueError, EvaluationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if trace.truthy:
        return RuleTestResult(passed=True, evidence=collect_fields(trace))
    return RuleTestResult(
        passed=False,
        explanation=explain_failure(trace),
        evidence=collect_fields(trace),
    )