import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user
from app.models.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
)


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=UserResponse)
def register_user(
    payload: UserRegister,
    db: Session = Depends(get_db),
):
    existing_user = crud.get_user_by_email(db, payload.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    user = crud.create_user(
        db=db,
        user_id=str(uuid.uuid4()),
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )

    return user


@auth_router.post("/login", response_model=TokenResponse)
def login_user(
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_email(db, payload.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(
        data={"sub": user.id}
    )

    return TokenResponse(access_token=token)


@auth_router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user