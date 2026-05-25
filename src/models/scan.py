from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.models import BaseModel, Base

class Scan(BaseModel):
    """Scan record model."""
    __tablename__ = "scans"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    project_name = Column(String(255))
    repo_url = Column(String(2048))
    status = Column(String(50), default="pending")  # pending, running, complete, failed
    file_count = Column(Integer)
    repo_size_mb = Column(Float)
    primary_language = Column(String(50))
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    error_message = Column(String(512))

    # Relationships
    user = relationship("User", back_populates="scans")
    result = relationship("Result", back_populates="scan", uselist=False, cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="scan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scan {self.id} - {self.status}>"
