from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.chat_service import get_chat_response

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/ask", response_model=ChatResponse)
def ask_chat(request: ChatRequest, db: Session = Depends(get_db)):
    answer = get_chat_response(request.message, db)
    return ChatResponse(answer=answer)

@router.get("/ask")
def chat_info():
    return {"message": "Chatbot endpoint is active. Please use POST with a 'message' field to ask questions."}
