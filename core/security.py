from datetime import datetime, timedelta, time
from typing import Optional

from core.config import settings
from jose import jwt
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


def next_midnight_utc() -> datetime:
    now = datetime.now()
    tomorrow = (now.date() + timedelta(days=1))
    expiry = datetime.combine(tomorrow, time(0, 0))
    return expiry


def create_access_token(subject: int, expires_delta_minutes: Optional[int] = None) -> tuple[str, int]:
    if expires_delta_minutes:
        exp = datetime.now() + timedelta(minutes=expires_delta_minutes)
    else:
        exp = next_midnight_utc()
    payload = {"sub": str(subject), "exp": int(exp.timestamp())}
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return token, int(exp.timestamp())


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
