import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import ALGORITHM, SECRET_KEY, create_access_token, create_refresh_token
from app.schemas.user import AccessTokenResponse, TokenResponse, RefreshTokenRequest
from app.services import user_service
from app.services.user_service import get_user_by_email

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

    access_token = create_access_token(
        data={
            "sub": existing_user.email,
            "token_version": existing_user.token_version,
        }
    )

    refresh_token = create_refresh_token(
        {
            "sub": existing_user.email,
            "token_version": existing_user.token_version,
        }
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_access_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            request.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        token_type = payload.get("type")
        email = payload.get("sub")
        token_version = payload.get("token_version")

        if token_type != "refresh" or email is None or token_version is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = get_user_by_email(db, email=email)

    if user is None or not user.is_active or token_version != user.token_version:
        raise credentials_exception

    access_token = create_access_token(
        {
            "sub": user.email,
            "token_version": user.token_version,
        }
    )

    return AccessTokenResponse(
        access_token=access_token,
    )
