from app.services.rag_service import RAGService
from app.services.llm_service import LLMService

class ChatService:
    def __init__(self):
        self.rag_service = RAGService()
        self.llm_service = LLMService()

    async def chat(self, query: str, user_id: str) -> dict:
        # Step 1 — retrieve relevant chunks from ChromaDB
        context_chunks = await self.rag_service.retrieve(
            query=query,
            user_id=user_id
        )

        # Step 2 — generate answer using Gemini
        answer = await self.llm_service.generate_answer(
            query=query,
            context_chunks=context_chunks
        )

        # Step 3 — return answer + the source chunks (for transparency)
        return {
            "answer": answer,
            "sources": context_chunks
        }