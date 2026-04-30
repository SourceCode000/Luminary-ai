from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()


class EmbeddingService:

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-3-small"

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Convert a list of text chunks into vectors.
        Used during document ingestion.
        """
        if not texts:
            return []

        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        # extract the vector from each result
        return [item.embedding for item in response.data]

    async def embed_query(self, query: str) -> list[float]:
        """
        Convert a single query string into a vector.
        Used during chat when searching ChromaDB.
        """
        response = await self.client.embeddings.create(
            model=self.model,
            input=[query],
        )
        return response.data[0].embedding