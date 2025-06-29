from typing import Optional
from fastapi import Depends, Request, HTTPException, Response
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
from datetime import datetime, timezone
from app.db.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
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

    # 检查会员到期
    async def on_after_login(
            self, user: User, request: Request | None = None, response: Response | None = None,
            ):
        session: AsyncSession = await get_async_session().__anext__()
        if user.is_premium and user.premium_end_at and user.premium_end_at < datetime.now():
            user.is_premium = False
            await session.commit()

# 👉 依赖注入，FastAPI 用它来获取用户管理器
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)



# 🚪 Bearer Token 登录（适合 API 调用）
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# 🍪 Cookie 登录（适合前后端一起使用）

is_production = True # settings.APP_ENV = 'production'

cookie_transport = CookieTransport(
    cookie_name="auth_cookie", 
    cookie_max_age=36000, 
    cookie_samesite="none" if is_production else "lax", 
    cookie_domain=settings.COOKIE_DOMAIN if is_production else None, 
    cookie_secure=is_production)

# 🔑 JWT 策略（用于生成 token）
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=36000)

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
current_active_user_optional = fastapi_users.current_user(active=True, optional=True)
current_super_user = fastapi_users.current_user(superuser=True)

# 自定义验证身份依赖

async def get_premium_user(user: User =Depends(current_active_user)):
    if not user.is_premium:
        raise HTTPException(status_code=403, detail="您还不是会员，请联系管理员升级会员")
    return user
