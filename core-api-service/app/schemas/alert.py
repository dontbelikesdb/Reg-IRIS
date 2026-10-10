
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class Alert(BaseModel):
    id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.OPEN

    category: str
    source_document: str | None = None
    rule_name: str | None = None

    created_at: datetime
    updated_at: datetime

    metadata: dict = Field(default_factory=dict)


class AlertListResponse(BaseModel):
    items: list[Alert]
    total: int
    limit: int


class AlertSummary(BaseModel):
    total: int
    open: int
    acknowledged: int
    resolved: int
    critical: int
    high: int
