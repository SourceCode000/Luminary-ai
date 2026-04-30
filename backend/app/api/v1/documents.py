from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.document_service import DocumentService
from app.schemas.document import DocumentUploadResponse, DocumentListResponse
from app.core.exceptions import DocumentNotFound

router = APIRouter(prefix="/documents", tags=["Documents"])


# ── Upload Document ────────────────────────────────────────────────

@router.post("", response_model=DocumentUploadResponse, status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a document and trigger the ingestion pipeline."""
    service = DocumentService(db)
    document = await service.ingest_document(
        file=file,
        user_id=current_user.id,
    )
    return document


# ── List Documents ─────────────────────────────────────────────────

@router.get("", response_model=list[DocumentListResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all documents for the current user."""
    service = DocumentService(db)
    return await service.list_documents(current_user.id)


# ── Delete Document ────────────────────────────────────────────────

@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document and all its vectors."""
    service = DocumentService(db)
    await service.delete_document(document_id, current_user.id)