from core.security import hash_password, verify_password
from db.models.group import Group
from db.models.user import User
from sqlalchemy.orm import Session


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, username: str, email: str, password: str, groups: list[str] = None):
    user = User(username=username, email=email, password_hash=hash_password(password))
    if groups:
        g_objs = db.query(Group).filter(Group.name.in_(groups)).all()
        user.groups = g_objs
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
