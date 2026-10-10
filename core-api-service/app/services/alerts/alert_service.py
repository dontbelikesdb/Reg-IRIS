
from datetime import datetime, timezone

from app.schemas.alert import (
    Alert,
    AlertSeverity,
    AlertStatus,
    AlertSummary,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_demo_alerts() -> list[Alert]:
    now = utc_now()

    return [
        Alert(
            id="ALT-001",
            title="Critical regulatory deadline approaching",
            description=(
                "A regulatory obligation has a short remaining "
                "time window and requires immediate review."
            ),
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.OPEN,
            category="Regulatory Deadline",
            source_document="EU_Regulatory_Obligations.pdf",
            rule_name="DeadlineProximityRule",
            created_at=now,
            updated_at=now,
            metadata={
                "regulator": "ESMA",
                "days_remaining": 2,
                "department": "Compliance",
            },
        ),
        Alert(
            id="ALT-002",
            title="Potential regulatory policy conflict",
            description=(
                "A newly published requirement may conflict "
                "with an existing internal compliance policy."
            ),
            severity=AlertSeverity.HIGH,
            status=AlertStatus.ACKNOWLEDGED,
            category="Policy Conflict",
            source_document="MiFID_II_Updates.pdf",
            rule_name="PolicyConflictRule",
            created_at=now,
            updated_at=now,
            metadata={
                "regulator": "ESMA",
                "department": "Legal",
                "review_required": True,
            },
        ),
        Alert(
            id="ALT-003",
            title="Regulatory document requires review",
            description=(
                "A regulatory update has been flagged for "
                "a compliance team's manual review."
            ),
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.OPEN,
            category="Document Review",
            source_document="AML_Guidelines.pdf",
            rule_name="DocumentReviewRule",
            created_at=now,
            updated_at=now,
            metadata={
                "regulator": "EBA",
                "department": "AML Compliance",
            },
        ),
    ]


# In-memory store: deliberately temporary mock data.
_alerts: dict[str, Alert] = {
    alert.id: alert for alert in create_demo_alerts()
}


def list_alerts(
    status: AlertStatus | None = None,
    severity: AlertSeverity | None = None,
    limit: int = 50,
) -> list[Alert]:
    results = list(_alerts.values())

    if status is not None:
        results = [a for a in results if a.status == status]

    if severity is not None:
        results = [a for a in results if a.severity == severity]

    results.sort(
        key=lambda alert: alert.created_at,
        reverse=True,
    )

    return results[:limit]


def get_alert(alert_id: str) -> Alert | None:
    return _alerts.get(alert_id)


def acknowledge_alert(alert_id: str) -> Alert | None:
    alert = _alerts.get(alert_id)

    if alert is None:
        return None

    if alert.status == AlertStatus.RESOLVED:
        raise ValueError("A resolved alert cannot be acknowledged.")

    alert.status = AlertStatus.ACKNOWLEDGED
    alert.updated_at = utc_now()

    return alert


def resolve_alert(alert_id: str) -> Alert | None:
    alert = _alerts.get(alert_id)

    if alert is None:
        return None

    alert.status = AlertStatus.RESOLVED
    alert.updated_at = utc_now()

    return alert


def get_alert_summary() -> AlertSummary:
    alerts = list(_alerts.values())

    return AlertSummary(
        total=len(alerts),
        open=sum(a.status == AlertStatus.OPEN for a in alerts),
        acknowledged=sum(
            a.status == AlertStatus.ACKNOWLEDGED for a in alerts
        ),
        resolved=sum(
            a.status == AlertStatus.RESOLVED for a in alerts
        ),
        critical=sum(
            a.severity == AlertSeverity.CRITICAL for a in alerts
        ),
        high=sum(
            a.severity == AlertSeverity.HIGH for a in alerts
        ),
    )
