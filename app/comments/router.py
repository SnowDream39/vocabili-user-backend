# comments/api.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from typing import List

from app.db.session import get_async_session
from app.users.manager import current_active_user
from app.db.models import Comment
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
        #created_at=datetime.now(tz=timezone.utc),
        parent_id=comment.parent_id,
        article_id=comment.article_id
        )
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment

@router.get("/", response_model=List[CommentRead])
async def list_comments(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Comment).options(joinedload(Comment.user))
    result = await session.execute(stmt)
    comments = result.scalars().all()
    return [
        CommentRead(
            id=c.id,
            content=c.content,
            user_id=c.user_id,
            article_id=c.article_id,
            parent_id=c.parent_id,
            username=c.user.username if c.user else None,
        )
        for c in comments
    ]

@router.get("/by_article/{article_id}", response_model=List[CommentRead])
async def list_comments_by_article(
    article_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Comment).options(joinedload(Comment.user)).where(Comment.article_id == article_id)
    result = await session.execute(stmt)
    comments = result.scalars().all()

    return [
        CommentRead(
            id=c.id,
            content=c.content,
            user_id=c.user_id,
            article_id=c.article_id,
            parent_id=c.parent_id,
            username=c.user.username if c.user else None,
        )
        for c in comments
    ]