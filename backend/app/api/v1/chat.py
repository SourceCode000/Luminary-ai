from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["Chat"])
chat_service = ChatService()

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    result = await chat_service.chat(
        query=request.query,
        user_id=str(current_user.id)
    )
    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )