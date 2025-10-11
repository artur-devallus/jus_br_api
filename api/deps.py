from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from core.security import decode_token
from db.session import get_db
from db.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


def require_group(name: str):
    def inner(user: User = Depends(get_current_user)):
        if name not in [g.name for g in user.groups]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return inner
