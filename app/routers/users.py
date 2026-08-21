from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service

from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)
