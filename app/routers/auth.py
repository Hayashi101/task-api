from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from app.schemas.user import TokenResponse
from app.services import user_service

from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def authenticate_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    existing_user = user_service.authenticate_user(
        db, form_data.username, form_data.password
    )

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": existing_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
