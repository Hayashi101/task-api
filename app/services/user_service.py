from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Literal

from app.core.exceptions import UserAlreadyExistsError
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


def commit_or_raise_duplicate(db: Session):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise UserAlreadyExistsError() from exc


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def create_user(db: Session, user: UserCreate):
    existing_user = get_user_by_email(db, user.email)

    if existing_user is not None:
        raise UserAlreadyExistsError()

    hashed_password = hash_password(user.password)

    new_user = User(email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    commit_or_raise_duplicate(db)
    db.refresh(new_user)

    return new_user
