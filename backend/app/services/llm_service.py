from groq import AsyncGroq
from app.config import get_settings

settings = get_settings()

class LLMService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = "llama-3.3-70b-versatile"

    async def generate_answer(self, query: str, context_chunks: list[str]) -> str:
        if not context_chunks:
            return "I couldn't find any relevant information in your documents to answer that question."

        context = "\n\n".join(context_chunks)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are Luminary, an intelligent document assistant. Use ONLY the provided context to answer questions. If the answer is not in the context, say 'I don't have enough information in your documents to answer that.'"
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}"
                }
            ]
        )
        return response.choices[0].message.content