from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.db.connection import get_db
from src.models import User
from src.api.utils import create_access_token, create_refresh_token
from sqlalchemy.orm import Session
from datetime import timedelta

router = APIRouter()

class LoginRequest(BaseModel):
    oauth_provider: str  # 'google' or 'github'
    oauth_id: str
    email: str
    name: str
    oauth_token: str
    picture_url: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """OAuth2 login endpoint."""

    # Check if user exists
    user = db.query(User).filter(User.oauth_id == request.oauth_id).first()

    if not user:
        # Create new user
        user = User(
            email=request.email,
            name=request.name,
            oauth_provider=request.oauth_provider,
            oauth_id=request.oauth_id,
            oauth_token=request.oauth_token,
            picture_url=request.picture_url
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update existing user
        user.oauth_token = request.oauth_token
        user.oauth_provider = request.oauth_provider
        db.commit()

    # Generate tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "oauth_provider": user.oauth_provider,
            "picture_url": user.picture_url
        }
    )

@router.post("/refresh")
async def refresh(refresh_token: str):
    """Refresh access token."""
    from src.api.utils import verify_token

    payload = verify_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    new_access_token = create_access_token(data={"sub": user_id})

    return {"access_token": new_access_token, "token_type": "bearer"}

@router.get("/me")
async def get_current_user(user: User = Depends(lambda: None)):
    """Get current authenticated user."""
    from src.api.auth import get_current_user
    from fastapi.security import HTTPBearer

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "oauth_provider": user.oauth_provider
    }
