import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.db.connection import get_db
from src.models import User, Scan, Result
from src.api.auth import get_current_user
from sqlalchemy.orm import Session
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

class ResultCreate(BaseModel):
    scan_id: str
    code_snippet: str | None = None
    semgrep_json: dict | None = None
    llm_analysis: str | None = None
    patches: str | None = None
    severity_count: dict | None = None

class ResultResponse(BaseModel):
    id: str
    scan_id: str
    code_snippet: str | None
    semgrep_json: dict | None
    llm_analysis: str | None
    patches: str | None
    severity_count: dict | None
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/{scan_id}", response_model=ResultResponse)
async def save_result(
    scan_id: str,
    result_data: ResultCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save analysis results."""
    logger.info(f"User {user.id} saving results for scan {scan_id}")

    # Verify scan belongs to user
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == user.id
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Delete existing result if any
    existing = db.query(Result).filter(Result.scan_id == scan_id).first()
    if existing:
        db.delete(existing)

    # Create new result
    result = Result(
        scan_id=scan_id,
        code_snippet=result_data.code_snippet,
        semgrep_json=result_data.semgrep_json,
        llm_analysis=result_data.llm_analysis,
        patches=result_data.patches,
        severity_count=result_data.severity_count
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    return result

@router.get("/{scan_id}", response_model=ResultResponse)
async def get_result(
    scan_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analysis results for a scan."""

    # Verify scan belongs to user
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == user.id
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    result = db.query(Result).filter(Result.scan_id == scan_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Results not found")

    return result
