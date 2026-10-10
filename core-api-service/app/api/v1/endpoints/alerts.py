
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.alert import (
    Alert,
    AlertListResponse,
    AlertSeverity,
    AlertStatus,
    AlertSummary,
)
from app.services.alerts import alert_service


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.get(
    "/summary",
    response_model=AlertSummary,
)
def get_summary():
    return alert_service.get_alert_summary()


@router.get(
    "",
    response_model=AlertListResponse,
)
def get_alerts(
    status_filter: AlertStatus | None = Query(
        default=None,
        alias="status",
    ),
    severity: AlertSeverity | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
):
    items = alert_service.list_alerts(
        status=status_filter,
        severity=severity,
        limit=limit,
    )

    return AlertListResponse(
        items=items,
        total=len(items),
        limit=limit,
    )


@router.get(
    "/{alert_id}",
    response_model=Alert,
)
def get_alert(alert_id: str):
    alert = alert_service.get_alert(alert_id)

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    return alert


@router.post(
    "/{alert_id}/acknowledge",
    response_model=Alert,
)
def acknowledge_alert(alert_id: str):
    try:
        alert = alert_service.acknowledge_alert(alert_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    return alert


@router.post(
    "/{alert_id}/resolve",
    response_model=Alert,
)
def resolve_alert(alert_id: str):
    alert = alert_service.resolve_alert(alert_id)

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    return alert
