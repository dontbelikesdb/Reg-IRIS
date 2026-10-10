from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from starlette.concurrency import run_in_threadpool

from app.schemas.impact import ImpactReport
from app.schemas.internal import ServiceError
from app.schemas.rule import RegulatorInfo, RegulatorListResponse, RuleInfo
from app.services.impact.csv_exporter import report_to_csv
from app.services.impact.impact_evaluator import build_report
from app.services.impact.trade_loader import parse_trades, read_upload
from app.services.rules.rule_loader import list_regulators, load_regulators

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


def _run_check(content: bytes, regulator_ids: list[str]) -> ImpactReport:
    rulesets = load_regulators(regulator_ids)  # fail fast on a bad regulator
    parsed = parse_trades(content)
    return build_report(parsed, rulesets)


@router.post("/impact/check", response_model=ImpactReport)
async def check_trades(
    file: UploadFile = File(...),
    regulators: list[str] = Form(...),  # send repeated fields or "EMIR,FCA"
):
    ids = [part.strip() for item in regulators for part in item.split(",") if part.strip()]
    try:
        content = await read_upload(file)
        return await run_in_threadpool(_run_check, content, ids)
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