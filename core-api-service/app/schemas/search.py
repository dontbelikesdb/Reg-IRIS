from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class DocumentMetadata(BaseModel):
    document_id: str  # maps to 'document' in your image
    file_name: str
    regulator: str
    jurisdiction: str
    effective_date: date
    category: str
    version: int
    upload_time: datetime
    parent_doc_id: Optional[str] = None