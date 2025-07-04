from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.users.router import router as users_router
from app.comments.router import router as comments_router  # 未来模块
from app.likes.router import router as likes_router
from app.users.admin_router import router as admin_router

from config import settings

app = FastAPI(root_path=settings.ROOT)

# 全局中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://vocabili.top", "https://api.vocabili.top"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载子路由
app.include_router(users_router)
app.include_router(comments_router)
app.include_router(likes_router)
app.include_router(admin_router, prefix="/admin", tags=["admin"])
