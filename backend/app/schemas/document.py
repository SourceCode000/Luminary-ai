from pydantic import BaseModel
from datetime import datetime
from app.models.document import DocumentStatus


# ── Responses (what we send back to the user) ──────────────────────

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    status: DocumentStatus
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    status: DocumentStatus
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True