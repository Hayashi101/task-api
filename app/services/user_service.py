from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Literal

from app.core.exceptions import (
    InvalidCurrentPasswordError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, ChangePasswordRequest


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


def authenticate_user(db: Session, email: str, password: str):
    existing_user = get_user_by_email(db, email)

    if existing_user is None or not existing_user.is_active:
        return None

    verified_password = verify_password(password, existing_user.hashed_password)

    if not verified_password:
        return None

    return existing_user


def change_password(
    db: Session,
    user: User,
    password_data: ChangePasswordRequest,
):

    verified_password = verify_password(
        password_data.current_password, user.hashed_password
    )

    if not verified_password:
        raise InvalidCurrentPasswordError()

    user.hashed_password = hash_password(password_data.new_password)

    db.commit()



def get_users(db: Session):
    return  db.scalars(select(User)).all()


def get_user_by_id(user_id: int, db: Session) -> User | None:
    existing_user = db.scalar(select(User).where(User.id == user_id))
    
    if existing_user is None:
        return None
    
    return existing_user 

def deactivate_user(db: Session, user_id: int) -> None:
    user = get_user_by_id(user_id, db)
    
    if user is None:
        raise UserNotFoundError
    
    user.is_active = False
    db.commit()
    