from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.models import BaseModel, Base

class ChatMessage(BaseModel):
    """Chat message model for conversation history."""
    __tablename__ = "chat_messages"

    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    # Relationships
    scan = relationship("Scan", back_populates="chat_messages")

    def __repr__(self):
        return f"<ChatMessage {self.scan_id} - {self.role}>"
