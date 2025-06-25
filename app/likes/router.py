from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from app.db.models import Like, User, Comment
from app.db.session import get_async_session
from app.users.manager import current_active_user

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.likes.schemas import LikeCreate, LikeRead, LikeDelete
from datetime import datetime, timezone

router = APIRouter(prefix="/likes", tags=["likes"])

@router.post("", response_model=LikeRead)
async def create_like(
    like: LikeCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    new_like = Like(
        comment_id=like.comment_id,
        user_id=current_user.id,
        created_at=datetime.now(tz=timezone.utc),
    )
    session.add(new_like)
    await session.commit()
    await session.refresh(new_like)
    return new_like

@router.delete("", response_model=LikeRead)
async def delete_like(
    like: LikeDelete,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    like_obj = await session.execute(
        select(Like).where(
            Like.comment_id == like.comment_id,
            Like.user_id == current_user.id,
        )
    )
    like_obj = like_obj.scalars().first()
    if not like_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found",
        )
    else:
        await session.delete(like_obj)
        await session.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Like deleted"})

