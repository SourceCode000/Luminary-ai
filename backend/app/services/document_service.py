import os
import shutil
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import chromadb

from app.config import get_settings
from app.models.document import DocumentStatus
from app.db.repositories.document_repository import DocumentRepository
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService

settings = get_settings()

# ── ChromaDB Client ────────────────────────────────────────────────

chroma_client = chromadb.HttpClient(
    host=settings.chroma_host,
    port=settings.chroma_port,
)

UPLOAD_DIR = "uploads"


class DocumentService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.chunker = ChunkingService()
        self.embedder = EmbeddingService()

    # ── Upload + Ingest ────────────────────────────────────────────

    async def ingest_document(
        self,
        file: UploadFile,
        user_id: str,
    ):
        """
        Full ingestion pipeline:
        1. Save file to disk
        2. Create document record in PostgreSQL
        3. Extract text + chunk it
        4. Embed chunks
        5. Store in ChromaDB
        6. Update document status
        """

        # get file type from extension
        file_type = file.filename.split(".")[-1].lower()
        if file_type not in ["pdf", "docx", "txt"]:
            raise ValueError(f"Unsupported file type: {file_type}")

        # 1. save file to disk
        user_upload_dir = os.path.join(UPLOAD_DIR, user_id)
        os.makedirs(user_upload_dir, exist_ok=True)
        file_path = os.path.join(user_upload_dir, file.filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 2. create document record in PostgreSQL
        document = await self.doc_repo.create(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_type=file_type,
        )

        # 3. update status to processing
        await self.doc_repo.update_status(
            document.id,
            DocumentStatus.PROCESSING,
        )

        try:
            # 4. extract text and chunk it
            chunks = self.chunker.process(file_path, file_type)

            if not chunks:
                raise ValueError("No text could be extracted from the file.")

            # 5. embed all chunks
            vectors = await self.embedder.embed_texts(chunks)

            # 6. store in ChromaDB
            collection = chroma_client.get_or_create_collection(
                name=f"user_{user_id}"
            )

            collection.add(
                ids=[f"{document.id}_chunk_{i}" for i in range(len(chunks))],
                embeddings=vectors,
                documents=chunks,
                metadatas=[{
                    "document_id": document.id,
                    "filename": file.filename,
                    "chunk_index": i,
                } for i in range(len(chunks))]
            )

            # 7. update status to ready
            await self.doc_repo.update_status(
                document.id,
                DocumentStatus.READY,
                chunk_count=len(chunks),
            )

        except Exception as e:
            # if anything fails, mark as failed
            await self.doc_repo.update_status(
                document.id,
                DocumentStatus.FAILED,
            )
            raise e

        return document

    # ── List Documents ─────────────────────────────────────────────

    async def list_documents(self, user_id: str):
        """Get all documents for a user."""
        return await self.doc_repo.list_by_user(user_id)

    # ── Delete Document ────────────────────────────────────────────

    async def delete_document(self, document_id: str, user_id: str):
        """
        Delete a document from:
        1. ChromaDB (vectors)
        2. Disk (file)
        3. PostgreSQL (record)
        """
        document = await self.doc_repo.get_by_id(document_id)

        if not document:
            from app.core.exceptions import DocumentNotFound
            raise DocumentNotFound(document_id)

        if document.user_id != user_id:
            from app.core.exceptions import UnauthorizedAccess
            raise UnauthorizedAccess()

        # 1. delete from ChromaDB
        try:
            collection = chroma_client.get_or_create_collection(
                name=f"user_{user_id}"
            )
            collection.delete(
                where={"document_id": document_id}
            )
        except Exception:
            pass  # if ChromaDB delete fails, continue anyway

        # 2. delete file from disk
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        # 3. delete from PostgreSQL
        await self.doc_repo.delete(document_id)