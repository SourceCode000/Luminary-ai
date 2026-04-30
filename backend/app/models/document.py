import uuid
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import mapped_column, MappedColumn, relationship
from app.models.base import Base, TimestampMixin
import enum


# ── Document Status ────────────────────────────────────────────────

class DocumentStatus(enum.Enum):
    PENDING    = "pending"      # just uploaded, not processed yet
    PROCESSING = "processing"   # currently being chunked and embedded
    READY      = "ready"        # fully processed, ready to search
    FAILED     = "failed"       # something went wrong during processing


# ── Document Model ─────────────────────────────────────────────────

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: MappedColumn[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: MappedColumn[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False, index=True
    )
    filename: MappedColumn[str] = mapped_column(
        String, nullable=False
    )
    file_path: MappedColumn[str] = mapped_column(
        String, nullable=False                  # where the file is saved on disk
    )
    file_type: MappedColumn[str] = mapped_column(
        String, nullable=False                  # pdf, docx, txt
    )
    status: MappedColumn[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus),
        default=DocumentStatus.PENDING,
        nullable=False
    )
    chunk_count: MappedColumn[int] = mapped_column(
        Integer, default=0                      # updated after processing
    )

    # relationship — lets you do document.user to get the user object
    user = relationship("User", backref="documents")