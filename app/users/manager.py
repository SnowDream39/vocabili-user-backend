from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, models, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from config import settings
from app.users.db import User, get_user_db  # 你的用户模型和依赖
from config import SECRET  # 推荐放到 config 文件中管理密钥

# 🔒 自定义用户管理器，主键类型为 int（不是 UUID！）
class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} forgot password. Token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Token: {token}")

# 👉 依赖注入，FastAPI 用它来获取用户管理器
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

# 🚪 Bearer Token 登录（适合 API 调用）
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# 🍪 Cookie 登录（适合前后端一起使用）

is_production = True # settings.APP_ENV = 'production'

cookie_transport = CookieTransport(
    cookie_name="auth_cookie", 
    cookie_max_age=3600, 
    cookie_samesite="None" if is_production else "Lax", 
    cookie_domain=settings.COOKIE_DOMAIN if is_production else None, 
    cookie_secure=is_production)

# 🔑 JWT 策略（用于生成 token）
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

# 🧊 创建认证后端：Bearer 和 Cookie 都支持
# 只需要再提供路径，就可以成为路由。它被路由直接使用。
auth_backend_bearer = AuthenticationBackend(
    name="jwt-bearer",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

auth_backend_cookie = AuthenticationBackend(
    name="jwt-cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

# 🔧 构建 FastAPI Users 核心对象（支持多个认证方式）
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend_bearer, auth_backend_cookie],  # 支持多种认证方式
)

# 🧍 当前登录并激活的用户依赖
current_active_user = fastapi_users.current_user(active=True)
