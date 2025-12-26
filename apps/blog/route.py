from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apps.authentication.models.models import User
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


# class PostCreateRouter(CreateRouter[Post, PostCreate]):
#     def create(self, item: PostCreate, db: Session = Depends(get_db)):
#         # check if author exists
#         author = db.query(User).filter(self.model.author_id == item.author_id).first()
#         if not author:
#             return StandardResponse.error_response(
#                 message="Author not found.",
#                 status_code=status.HTTP_400_BAD_REQUEST,
#             )
#         db_item = self.model(**item.model_dump())
#         db.add(db_item)
#         db.commit()
#         db.refresh(db_item)
#         return StandardResponse(
#             success=True,
#             data=self.schema.model_validate(db_item),
#             message="Post created successfully.",
#         )


class PostCreateRouter(CreateRouter[Post, PostCreate]):
    def create(self, item: PostCreate, db: Session = Depends(get_db)):
        author = db.query(User).filter(User.id == item.author_id).first()
        if not author:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=StandardResponse.error_response(
                    message="Author not found."
                ).model_dump(),
            )
        db_item = self.model(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return StandardResponse(
            success=True,
            data=PostRetrieve.model_validate(db_item),
            message="Post created successfully.",
        )


class PostListRouter(ReadRouter[Post, PostList]):
    # def read_all(self, db: Session = Depends(get_db)):
    #     items = db.query(self.model).all()
    #     data = [self.schema.model_validate(item) for item in items]
    #     return StandardResponse(
    #         success=True, data=data, message="Posts fetched successfully."
    #     )
    pass


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
        # tags=["posts"],
    ),
    PostRetrieveRouter(
        Post,
        PostRetrieve,
        prefix="/retrieve/{id}",
        # tags=["posts"],
    ),
    PostCreateRouter(
        Post,
        PostCreate,
        prefix="/create",
        # tags=["posts"],
    ),
    # ReadRouter(
    #     Post,
    #     PostList,
    #     prefix="/list",
    #     # tags=["posts"],
    # ),
]

for post_router in post_routers:
    router.include_router(post_router.router, prefix="/posts")
