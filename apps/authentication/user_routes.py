# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from apps.database import get_db
# from base.route import (
#     CreateRouter,
#     ReadRouter,
#     RetrieveRouter,
#     StandardResponse,
#     UpdateRouter,
# )

# from .models.models import User
# from .schemas import UserCreate, UserList, UserLogin, UserRetrieve, UserUpdate
# from .utils import hash_password, verify_password

# router = APIRouter()


# class UserCreateRouter(CreateRouter[User, UserCreate]):
#     def create(self, item: UserCreate, db: Session = Depends(get_db)):
#         # Check if user exists already
#         if (
#             db.query(self.model)
#             .filter(
#                 (self.model.username == item.username)
#                 | (self.model.email == item.email)
#             )
#             .first()
#         ):
#             raise HTTPException(
#                 status_code=400, detail="Username or email already registered."
#             )
#         db_item = self.model(
#             username=item.username,
#             email=item.email,
#             hashed_password=hash_password(item.password),
#         )
#         db.add(db_item)
#         db.commit()
#         db.refresh(db_item)
#         return StandardResponse(
#             success=True,
#             data=self.schema.model_validate(db_item),
#             message="User created successfully.",
#         )


# class UserReadRouter(ReadRouter[User, UserList]):
#     def read_all(self, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#         items = db.query(self.model).offset(skip).limit(limit).all()
#         data = [self.schema.model_validate(item) for item in items]
#         return StandardResponse(
#             success=True, data=data, message="Users fetched successfully."
#         )


# class UserRetrieveRouter(RetrieveRouter[User, UserRetrieve]):
#     def retrieve(self, user_id: int, db: Session = Depends(get_db)):
#         db_item = db.query(self.model).filter(self.model.id == user_id).first()
#         if not db_item:
#             raise HTTPException(status_code=404, detail="User not found.")
#         return StandardResponse(
#             success=True,
#             data=self.schema.model_validate(db_item),
#             message="User retrieved successfully.",
#         )


# @router.post("/login")
# def login(user: UserLogin, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.username == user.username).first()
#     if not db_user or not verify_password(user.password, db_user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid username or password.")
#     return {"message": "Login successful.", "username": db_user.username}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.database import get_db
from base.route import StandardResponse

from .models.models import User
from .schemas import UserCreate, UserList, UserLogin, UserRetrieve, UserUpdate
from .utils import hash_password, verify_password

router = APIRouter()


@router.post("/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user exists already
    existing_user = (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered.",
        )

    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return StandardResponse(
        success=True,
        data=UserRetrieve.model_validate(db_user),
        message="User created successfully.",
    )


@router.get("/", response_model=StandardResponse)
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get all users with pagination"""
    users = db.query(User).offset(skip).limit(limit).all()
    data = [UserList.model_validate(user) for user in users]

    return StandardResponse(
        success=True,
        data=data,
        message="Users fetched successfully.",
    )


@router.get("/{user_id}", response_model=StandardResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return StandardResponse(
        success=True,
        data=UserRetrieve.model_validate(user),
        message="User retrieved successfully.",
    )


@router.put("/{user_id}", response_model=StandardResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    # Update only provided fields
    update_data = user.model_dump(exclude_unset=True)

    # Hash password if it's being updated
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return StandardResponse(
        success=True,
        data=UserRetrieve.model_validate(db_user),
        message="User updated successfully.",
    )


@router.delete("/{user_id}", response_model=StandardResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    db.delete(db_user)
    db.commit()

    return StandardResponse(
        success=True,
        data=None,
        message="User deleted successfully.",
    )


@router.post("/login", response_model=StandardResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    return StandardResponse(
        success=True,
        data={
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
        },
        message="Login successful.",
    )
