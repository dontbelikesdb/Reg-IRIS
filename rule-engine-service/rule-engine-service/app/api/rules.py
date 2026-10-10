"""Read-only endpoints for browsing regulators and their rules."""
from fastapi import APIRouter, HTTPException

from app.schemas.internal import RuleSet, ServiceError
from app.schemas.rule import RegulatorInfo, RegulatorListResponse, RuleInfo
from app.services.rules.rule_loader import list_regulators, load_regulators

router = APIRouter(prefix="/api/regulators", tags=["rules"])


def _to_info(rs: RuleSet) -> RegulatorInfo:
    return RegulatorInfo(
        id=rs.id,
        name=rs.name,
        jurisdiction=rs.jurisdiction,
        rule_count=len(rs.rules),
        rules=[RuleInfo(id=r.id, description=r.description, impact=r.impact) for r in rs.rules],
    )


@router.get("", response_model=RegulatorListResponse)
def get_regulators():
    """Everything the UI needs to draw the regulator picker."""
    return RegulatorListResponse(regulators=[_to_info(rs) for rs in list_regulators()])


@router.get("/{regulator_id}", response_model=RegulatorInfo)
def get_regulator(regulator_id: str):
    """One regulator and its rules (id is case-insensitive, e.g. mifid)."""
    try:
        return _to_info(load_regulators([regulator_id])[0])
    except ServiceError as exc:
        status = 404 if exc.status_code == 422 else exc.status_code  # unknown id -> 404
        raise HTTPException(status_code=status, detail=exc.message)