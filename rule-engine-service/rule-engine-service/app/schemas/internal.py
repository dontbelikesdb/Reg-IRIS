"""Internal (non-API) models shared by the rules and impact services."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ServiceError(Exception):
    """Raised by services; the API layer turns it into an HTTP error."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True)
class Rule:
    id: str
    description: str
    impact: str
    logic: Any  # raw JSON Logic, kept exactly as written in the rule file


@dataclass(frozen=True)
class RuleSet:
    id: str  # e.g. "MIFID" (taken from the file name rules_mifid.json)
    name: str  # e.g. "MiFID II"
    jurisdiction: str
    rules: tuple[Rule, ...]


@dataclass
class Trace:
    """One evaluated node of a JSON Logic expression.

    The explanation builder walks this tree to say *why* a rule failed.
    """

    op: str
    value: Any
    label: str
    children: list[Trace] = field(default_factory=list)
    detail: dict[str, Any] = field(default_factory=dict)

    @property
    def truthy(self) -> bool:
        return bool(self.value)