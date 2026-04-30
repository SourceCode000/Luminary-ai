import chromadb
from app.config import get_settings
from app.services.embedding_service import EmbeddingService

settings = get_settings()

class RAGService:
    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port
        )
        self.embedding_service = EmbeddingService()

    async def retrieve(self, query: str, user_id: str, top_k: int = 6) -> list[str]:
        # Step 1 — embed the question
        query_vector = await self.embedding_service.embed_query(query)

        # Step 2 — get this user's ChromaDB collection
        collection = self.client.get_or_create_collection(f"user_{user_id}")

        # Step 3 — search for closest vectors
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )

        # Step 4 — return just the text chunks
        if not results["documents"] or not results["documents"][0]:
            return []

        return results["documents"][0]