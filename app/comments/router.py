# comments/api.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_async_session
from app.users.manager import current_active_user
from .models import Comment
from .schemas import CommentCreate, CommentRead

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=CommentRead)
async def create_comment(
    comment: CommentCreate,
    user=Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    new_comment = Comment(content=comment.content, user_id=user.id)
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment

@router.get("/", response_model=List[CommentRead])
async def list_comments(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Comment))
    comments = result.scalars().all()
    return [CommentRead.model_validate(comment) for comment in comments]