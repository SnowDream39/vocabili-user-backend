# comments/api.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_async_session
from app.users.manager import current_active_user
from .models import Comment
from .schemas import CommentCreate, CommentRead
from datetime import datetime, timezone

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=CommentRead)
async def create_comment(
    comment: CommentCreate,
    user=Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    new_comment = Comment(
        content=comment.content, 
        user_id=user.id,
        created_at=datetime.now(tz=timezone.utc),
        parent_id=comment.parent_id,
        article_id=comment.article_id
        )
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment

@router.get("/", response_model=List[CommentRead])
async def list_comments(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Comment))
    comments = result.scalars().all()
    return [CommentRead.model_validate(comment) for comment in comments]

@router.get("/by_article/{article_id}", response_model=List[CommentRead])
async def list_comments_by_article(article_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Comment).where(Comment.article_id == article_id))
    comments = result.scalars().all()
    return [CommentRead.model_validate(comment) for comment in comments]
