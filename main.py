# from fastapi import FastAPI

# from apps.authentication.route import router as auth_router
# from apps.blog.route import router as blog_router

# app = FastAPI()
# app.include_router(auth_router, prefix="/auth")
# app.include_router(blog_router, prefix="/blog")

from fastapi import APIRouter, FastAPI

from apps.authentication.route import router as auth_router
from apps.blog.route import router as blog_router

app = FastAPI()

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router, prefix="/auth")
v1_router.include_router(blog_router, prefix="/blog")

# v2_router = APIRouter(prefix="/api/v2")
# v2_router.include_router(auth_router, prefix="/auth", tags=["v2-auth"])
# v2_router.include_router(blog_router, prefix="/blog", tags=["v2-blog"])


app.include_router(v1_router)
# app.include_router(v2_router)
