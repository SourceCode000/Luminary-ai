from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()

class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-3-small"

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    async def embed_query(self, query: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=self.model,
            input=[query]
        )
        return response.data[0].embedding