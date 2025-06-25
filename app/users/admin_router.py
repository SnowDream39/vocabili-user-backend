from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import timedelta

from app.db.session import get_async_session
from app.db.models import User
from app.users.schemas import UserRead
from app.users.manager import current_super_user, get_user_manager

# 以下操作仅限管理员

router = APIRouter()


# 设置会员
@router.post("/set-premium")
async def set_premium(
    user_id: str = Query(..., description="要设置的用户ID"),
    days: int = Query(30, description="会员持续天数"),
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_super_user),
):
    # 查找目标用户
    result = await session.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(status_code=404, detail="用户未找到")

    # 设置会员信息
    target_user.is_premium = True
    target_user.premium_end_at += timedelta(days=days)

    await session.commit()
    return {
        "message": f"用户 {user_id} 已设置为会员，截止至 {target_user.premium_end_at.isoformat()}",
        "is_premium": target_user.is_premium,
        "premium_end_at": target_user.premium_end_at,
    }

# 设置管理员
@router.post("/set-admin")
async def set_admin(
    user_id: str = Query(..., description="要设置管理员的用户ID"),
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_super_user),
):
    result = await session.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    target_user.is_superuser = True
    await session.commit()
    return {"message": f"用户 {user_id} 已设置为管理员"}

# 取消管理员
@router.post("/unset-admin")
async def unset_admin(
    user_id: str = Query(..., description="要取消管理员的用户ID"),
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_super_user),
):
    result = await session.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    target_user.is_superuser = False
    await session.commit()
    return {"message": f"用户 {user_id} 被取消管理员身份"}

# 获取所有用户
@router.get("/list-users")
async def list_users(
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_super_user),
):
    stmt = (
        select(User)
        .order_by(desc(User.id))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await session.execute(stmt)
    users = result.scalars().all()
    return [
        UserRead.model_validate(u)
        for u in users
    ]
    

