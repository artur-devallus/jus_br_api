from datetime import datetime, timedelta, time
from typing import Optional

from dateutil.tz import UTC

from core.config import settings
from jose import jwt, JWTError
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
MAX_BCRYPT_BYTES = 72


def hash_password(password: str) -> str:
    """Gera hash seguro da senha (limite bcrypt: 72 bytes)."""
    if not isinstance(password, str):
        raise TypeError("Password must be a string.")
    password = password.strip()
    if len(password.encode("utf-8")) > MAX_BCRYPT_BYTES:
        raise ValueError("Password exceeds bcrypt 72-byte limit.")
    return pwd_ctx.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Valida senha em texto puro contra hash armazenado."""
    if not isinstance(plain, str):
        raise TypeError("Password must be a string.")
    plain = plain.strip()
    return pwd_ctx.verify(plain, hashed)


def next_midnight_utc() -> datetime:
    """Retorna datetime UTC para meia-noite do próximo dia."""
    now = datetime.now(tz=UTC)
    tomorrow = (now.date() + timedelta(days=1))
    return datetime.combine(tomorrow, time(0, 0))


def create_access_token(subject: int, expires_delta_minutes: Optional[int] = None) -> tuple[str, int]:
    """Cria JWT com expiração configurável ou até meia-noite."""
    now = datetime.now(tz=UTC)
    if expires_delta_minutes:
        exp = now + timedelta(minutes=expires_delta_minutes)
    else:
        exp = next_midnight_utc()

    payload = {"sub": str(subject), "exp": int(exp.timestamp())}
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return token, int(exp.timestamp())


def decode_token(token: str) -> dict:
    """Decodifica JWT e valida assinatura."""
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token.")
