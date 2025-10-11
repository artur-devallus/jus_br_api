from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: dict, db: Session = Depends(get_db)):
    # expecting {"username": "...", "password": "..."}
    username = form_data.get("username")
    password = form_data.get("password")
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token, exp_ts = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer", "expires_at": str(exp_ts)}
