# from fastapi import FastAPI

# from apps.authentication.route import router as auth_router
# from apps.blog.route import router as blog_router

# app = FastAPI()
# app.include_router(auth_router, prefix="/auth")
# app.include_router(blog_router, prefix="/blog")

from fastapi import APIRouter, FastAPI

from apps.api_logs.middleware import APILoggingMiddleware
from apps.api_logs.route import router as api_logs_router
from apps.authentication.auth_routes import router as auth_router
from apps.authentication.user_routes import router as user_router
from apps.blog.route import router as blog_router
from apps.stock.route import router as stock_router

app = FastAPI()
app.add_middleware(APILoggingMiddleware)
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
v1_router.include_router(user_router, prefix="/users", tags=["Users"])
v1_router.include_router(blog_router, prefix="/blog", tags=["Blog"])
v1_router.include_router(stock_router, prefix="/stocks", tags=["Stocks"])
v1_router.include_router(api_logs_router, prefix="/logs", tags=["API Logs"])

# v2_router = APIRouter(prefix="/api/v2")
# v2_router.include_router(auth_router, prefix="/auth", tags=["v2-auth"])
# v2_router.include_router(blog_router, prefix="/blog", tags=["v2-blog"])


app.include_router(v1_router)
# app.include_router(v2_router)
