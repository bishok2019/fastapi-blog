from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.database import get_db

from .models.models import User
from .schemas import UserCreate, UserLogin
from .utils import hash_password, verify_password

router = APIRouter()


@router.post("/users/", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    if (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    ):
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user


@router.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful", "username": db_user.username}
