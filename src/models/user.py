from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from src.models import BaseModel, Base

class User(BaseModel):
    """User account model."""
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    oauth_provider = Column(String(50))  # 'google' or 'github'
    oauth_id = Column(String(255), unique=True, index=True)
    oauth_token = Column(Text)
    picture_url = Column(String(512))  # Profile picture from OAuth

    # Relationships
    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.oauth_provider})>"
