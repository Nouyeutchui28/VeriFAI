from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from datetime import datetime
from src.db.connection import get_db
from src.models import User, Scan
from src.api.auth import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()

class ScanCreate(BaseModel):
    project_name: str | None = None
    repo_url: str | None = None

class ScanUpdate(BaseModel):
    status: str
    file_count: int | None = None
    repo_size_mb: float | None = None
    primary_language: str | None = None
    error_message: str | None = None

class ScanResponse(BaseModel):
    id: str
    user_id: str
    project_name: str | None
    repo_url: str | None
    status: str
    file_count: int | None
    repo_size_mb: float | None
    primary_language: str | None
    start_time: datetime | None
    end_time: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/submit", response_model=ScanResponse)
async def submit_scan(
    scan_data: ScanCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a new scan."""

    scan = Scan(
        user_id=user.id,
        project_name=scan_data.project_name,
        repo_url=scan_data.repo_url,
        status="pending",
        start_time=datetime.utcnow()
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    return scan

@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get scan details."""

    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == user.id
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return scan

@router.get("/history", response_model=List[ScanResponse])
async def get_scan_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get user's scan history."""

    scans = db.query(Scan).filter(
        Scan.user_id == user.id
    ).order_by(Scan.created_at.desc()).limit(limit).all()

    return scans

@router.patch("/{scan_id}", response_model=ScanResponse)
async def update_scan(
    scan_id: str,
    scan_update: ScanUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update scan status."""

    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == user.id
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan_update.status == "complete":
        scan.end_time = datetime.utcnow()

    scan.status = scan_update.status
    if scan_update.file_count is not None:
        scan.file_count = scan_update.file_count
    if scan_update.repo_size_mb is not None:
        scan.repo_size_mb = scan_update.repo_size_mb
    if scan_update.primary_language is not None:
        scan.primary_language = scan_update.primary_language
    if scan_update.error_message is not None:
        scan.error_message = scan_update.error_message

    db.commit()
    db.refresh(scan)

    return scan
