"""Reads an uploaded regulator rule file from a multipart request."""
from __future__ import annotations

from fastapi import UploadFile

from app.schemas.internal import ServiceError
from app.services.rules.rule_loader import MAX_RULE_FILE_BYTES


async def read_rule_upload(file: UploadFile) -> bytes:
    """Read at most MAX_RULE_FILE_BYTES (+1, to detect oversize) from an upload."""
    name = file.filename or "file"
    if not name.lower().endswith(".json"):
        raise ServiceError(f"{name}: please upload a .json rule file.", 415)
    content = await file.read(MAX_RULE_FILE_BYTES + 1)
    if not content.strip():
        raise ServiceError(f"{name}: the uploaded file is empty.", 400)
    return content