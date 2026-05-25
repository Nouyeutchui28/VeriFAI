from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from src.db.connection import get_db
from src.models import User, Scan, ChatMessage
from src.api.auth import get_current_user
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter()

class ChatMessageCreate(BaseModel):
    scan_id: str
    role: str  # 'user' or 'assistant'
    content: str

class ChatMessageResponse(BaseModel):
    id: str
    scan_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=ChatMessageResponse)
async def save_message(
    message_data: ChatMessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save chat message."""

    # Verify scan belongs to user
    scan = db.query(Scan).filter(
        Scan.id == message_data.scan_id,
        Scan.user_id == user.id
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Create and save message
    message = ChatMessage(
        scan_id=message_data.scan_id,
        role=message_data.role,
        content=message_data.content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message

@router.get("/{scan_id}", response_model=List[ChatMessageResponse])
async def get_chat_history(
    scan_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a scan."""

    # Verify scan belongs to user
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == user.id
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    messages = db.query(ChatMessage).filter(
        ChatMessage.scan_id == scan_id
    ).order_by(ChatMessage.created_at).all()

    return messages
