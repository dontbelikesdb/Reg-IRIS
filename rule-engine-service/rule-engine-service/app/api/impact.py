from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from starlette.concurrency import run_in_threadpool

from app.schemas.impact import ImpactReport
from app.schemas.internal import ServiceError
from app.schemas.rule import RegulatorInfo, RegulatorListResponse, RuleInfo
from app.services.impact.csv_exporter import report_to_csv
from app.services.impact.impact_evaluator import build_report
from app.services.impact.trade_loader import parse_trades, read_upload
from app.services.rules.rule_loader import (
    MAX_CUSTOM_FILES, list_regulators, parse_uploaded_ruleset, resolve_rulesets,
)
from app.services.rules.rule_upload import read_rule_upload

router = APIRouter(prefix="/api", tags=["impact"])


@router.get("/regulators", response_model=RegulatorListResponse)
def get_regulators():
    return RegulatorListResponse(
        regulators=[
            RegulatorInfo(
                id=rs.id,
                name=rs.name,
                jurisdiction=rs.jurisdiction,
                rule_count=len(rs.rules),
                rules=[RuleInfo(id=r.id, description=r.description, impact=r.impact) for r in rs.rules],
            )
            for rs in list_regulators()
        ]
    )


def _run_check(content: bytes, regulator_ids: list[str], custom_rulesets: list) -> ImpactReport:
    rulesets = resolve_rulesets(regulator_ids, custom_rulesets)  # fail fast on a bad regulator
    parsed = parse_trades(content)
    return build_report(parsed, rulesets)


@router.post("/impact/check", response_model=ImpactReport)
async def check_trades(
    file: UploadFile = File(...),
    regulators: list[str] | None = Form(default=None),  # built-in ids: repeated fields or "EMIR,FCA"
    rule_files: list[UploadFile] | None = File(default=None),  # optional user-supplied rules_<name>.json
):
    ids = [part.strip() for item in regulators or [] for part in item.split(",") if part.strip()]
    uploads = rule_files or []
    try:
        if len(uploads) > MAX_CUSTOM_FILES:
            raise ServiceError(f"At most {MAX_CUSTOM_FILES} custom rule files per check.", 422)
        content = await read_upload(file)
        custom = [parse_uploaded_ruleset(f.filename, await read_rule_upload(f)) for f in uploads]
        return await run_in_threadpool(_run_check, content, ids, custom)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

@router.post("/impact/export")
def export_report(report: ImpactReport):
    """Send back the report JSON you got from /impact/check, get a CSV download."""
    return Response(
        content=report_to_csv(report),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="compliance_report.csv"'},
    )