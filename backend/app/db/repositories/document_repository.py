from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Document, DocumentStatus


class DocumentRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: str,
        filename: str,
        file_path: str,
        file_type: str,
    ) -> Document:
        """Save a new document record to the database."""
        document = Document(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
        )
        self.db.add(document)
        await self.db.flush()
        return document

    async def get_by_id(self, document_id: str) -> Document | None:
        """Find a document by its ID."""
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: str) -> list[Document]:
        """Get all documents belonging to a user."""
        result = await self.db.execute(
            select(Document).where(Document.user_id == user_id)
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        chunk_count: int = 0,
    ) -> None:
        """Update the processing status of a document."""
        document = await self.get_by_id(document_id)
        if document:
            document.status = status
            document.chunk_count = chunk_count
            await self.db.flush()

    async def delete(self, document_id: str) -> None:
        """Delete a document record from the database."""
        document = await self.get_by_id(document_id)
        if document:
            await self.db.delete(document)
            await self.db.flush()