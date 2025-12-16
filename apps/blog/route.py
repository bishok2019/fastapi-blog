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

from .models.post import Post
from .schemas import PostCreate, PostList, PostRetrieve, PostUpdate

router = APIRouter()

# create_router = CreateRouter(Post, PostCreate)
# read_router = ReadRouter(Post, PostList)
# retrieve_router = RetrieveRouter(Post, PostRetrieve)
# update_router = UpdateRouter(Post, PostUpdate, PostRetrieve)

# router.include_router(create_router.router, prefix="/posts", tags=["posts"])
# router.include_router(read_router.router, prefix="/posts", tags=["posts"])
# router.include_router(retrieve_router.router, prefix="/posts", tags=["posts"])
# router.include_router(update_router.router, prefix="/posts", tags=["posts"])


class PostCreateRouter(CreateRouter[Post, PostCreate]):
    def create(self, item: PostCreate, db: Session = Depends(get_db)):
        # check if author exists
        author = (
            db.query(self.model).filter(self.model.author_id == item.author_id).first()
        )
        if not author:
            raise HTTPException(status_code=400, detail="Author does not exist.")
        db_item = self.model(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return StandardResponse(
            success=True,
            data=self.schema.model_validate(db_item),
            message="Post created successfully.",
        )


class PostListRouter(ReadRouter[Post, PostList]):
    def read_all(self, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
        items = db.query(self.model).offset(skip).limit(limit).all()
        data = [self.schema.model_validate(item) for item in items]
        return StandardResponse(
            success=True, data=data, message="Posts fetched successfully."
        )


class PostRetrieveRouter(RetrieveRouter[Post, PostRetrieve]):
    def retrieve(self, id: int, db: Session = Depends(get_db)):
        db_item = db.query(self.model).filter(self.model.id == id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Post not found.")
        return StandardResponse(
            success=True,
            data=self.schema.model_validate(db_item),
            message="Post retrieved successfully.",
        )


post_routers = [
    PostListRouter(
        Post,
        PostList,
        prefix="/list",
        tags=["posts"],
    ),
    PostRetrieveRouter(
        Post,
        PostRetrieve,
        prefix="/retrieve/{id}",
        tags=["posts"],
    ),
    PostCreateRouter(
        Post,
        PostCreate,
        prefix="/create",
        tags=["posts"],
    ),
]

for post_router in post_routers:
    router.include_router(post_router.router, prefix="/posts", tags=["posts"])
