from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user, require_group
from db.session import get_db
from db.models.user import User
from schemas.auth import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_own(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "email": user.email, "is_active": user.is_active}


@router.get("/", dependencies=[Depends(require_group("admin"))])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
