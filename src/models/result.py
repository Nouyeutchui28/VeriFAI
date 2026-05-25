from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from src.models import BaseModel, Base

class Result(BaseModel):
    """Analysis result model."""
    __tablename__ = "results"

    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False, unique=True, index=True)
    code_snippet = Column(Text)  # First 5000 chars of analyzed code
    semgrep_json = Column(JSON)  # Full Semgrep results
    llm_analysis = Column(Text)  # LLM vulnerability analysis
    patches = Column(Text)  # Unified diff patches
    verification_status = Column(JSON)  # {"verified": bool, "details": dict}
    severity_count = Column(JSON)  # {"critical": 2, "high": 5, "medium": 10}

    # Relationships
    scan = relationship("Scan", back_populates="result")

    def __repr__(self):
        return f"<Result {self.scan_id}>"
