"""Read-only endpoints for browsing regulators and their rules."""
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.internal import RuleSet, ServiceError
from app.schemas.rule import RegulatorInfo, RegulatorListResponse, RuleInfo
from app.services.rules.rule_loader import list_regulators, load_regulators, parse_uploaded_ruleset
from app.services.rules.rule_upload import read_rule_upload

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

@router.post("/validate", response_model=RegulatorInfo)
async def validate_regulator_file(file: UploadFile = File(...)):
    """Check a user-supplied rules_<name>.json and preview what it contains.

    Nothing is saved. The UI keeps the file and sends it again with /api/impact/check.
    """
    try:
        return _to_info(parse_uploaded_ruleset(file.filename, await read_rule_upload(file)))
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
@router.get("/{regulator_id}", response_model=RegulatorInfo)
def get_regulator(regulator_id: str):
    """One regulator and its rules (id is case-insensitive, e.g. mifid)."""
    try:
        return _to_info(load_regulators([regulator_id])[0])
    except ServiceError as exc:
        status = 404 if exc.status_code == 422 else exc.status_code  # unknown id -> 404
        raise HTTPException(status_code=status, detail=exc.message)