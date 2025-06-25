from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.models import User
from app.users.manager import auth_backend_bearer, auth_backend_cookie, current_active_user, fastapi_users, current_super_user
from app.users.schemas import UserCreate, UserRead, UserUpdate




router = APIRouter()

# https://fastapi-users.github.io/fastapi-users/latest/configuration/routers/


# 登录，利用 backend


router.include_router(
    fastapi_users.get_auth_router(auth_backend_bearer), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(
    fastapi_users.get_auth_router(auth_backend_cookie), prefix="/auth/jwt-cookie", tags=["auth"]
)

# 其他

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

