from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from core.security import create_access_token
from crud.user import create_user, authenticate_user, get_user_by_username
from db.session import get_db
from schemas.auth import UserCreate, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, payload.username):
        raise HTTPException(400, "username already registered")
    user = create_user(db, username=payload.username, email=str(payload.email), password=payload.password)
    return {"id": user.id, "username": user.username}

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, exp = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer", "expires": exp}
