from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import User
from backend.app.api.auth import get_current_user
from backend.app.schemas.schemas import AIQueryRequest, AIQueryResponse
from backend.app.nlp.assistant import query_assistant

router = APIRouter(prefix="/ai", tags=["AI Assistant Chatbot"])

@router.post("/query", response_model=AIQueryResponse)
def execute_ai_query(request: AIQueryRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = query_assistant(db, request.query)
    return AIQueryResponse(
        answer=result["answer"],
        sources=result["sources"]
    )
