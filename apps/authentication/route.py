from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.database import get_db
from base.route import (
    CreateRouter,
    ReadRouter,
    RetrieveRouter,
    StandardResponse,
    UpdateRouter,
)

from .models.models import User
from .schemas import UserCreate, UserList, UserLogin, UserRetrieve, UserUpdate
from .utils import hash_password, verify_password

router = APIRouter()


class UserCreateRouter(CreateRouter[User, UserCreate]):
    def create(self, item: UserCreate, db: Session = Depends(get_db)):
        # Check if user exists already
        if (
            db.query(self.model)
            .filter(
                (self.model.username == item.username)
                | (self.model.email == item.email)
            )
            .first()
        ):
            raise HTTPException(
                status_code=400, detail="Username or email already registered."
            )
        db_item = self.model(
            username=item.username,
            email=item.email,
            hashed_password=hash_password(item.password),
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return StandardResponse(
            success=True,
            data=self.schema.model_validate(db_item),
            message="User created successfully.",
        )


class UserReadRouter(ReadRouter[User, UserList]):
    def read_all(self, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
        items = db.query(self.model).offset(skip).limit(limit).all()
        data = [self.schema.model_validate(item) for item in items]
        return StandardResponse(
            success=True, data=data, message="Users fetched successfully."
        )


class UserRetrieveRouter(RetrieveRouter[User, UserRetrieve]):
    def retrieve(self, user_id: int, db: Session = Depends(get_db)):
        db_item = db.query(self.model).filter(self.model.id == user_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="User not found.")
        return StandardResponse(
            success=True,
            data=self.schema.model_validate(db_item),
            message="User retrieved successfully.",
        )


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    return {"message": "Login successful.", "username": db_user.username}


user_routers = [
    UserCreateRouter(
        User,
        UserCreate,
        prefix="/create",
        tags=["users"],
    ),
    UserReadRouter(
        User,
        UserList,
        prefix="/list",
        tags=["users"],
    ),
    UserRetrieveRouter(
        User,
        UserRetrieve,
        prefix="/retrieve/{user_id}",
        tags=["users"],
    ),
    # UpdateRouter(
    #     User,
    #     UserUpdate,
    #     UserRetrieve,
    #     prefix="/update/{user_id}",
    #     tags=["users"],
    # ),
]

# router.include_router(user_routers.router)
for user_router in user_routers:
    router.include_router(user_router.router, prefix="/users")
