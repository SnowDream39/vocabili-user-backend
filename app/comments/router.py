# comments/api.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from sqlalchemy import desc
from typing import List
from collections import defaultdict

from app.db.session import get_async_session
from app.users.manager import current_active_user
from app.db.models import Comment, User, Like
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
    stmt = select(Comment).options(joinedload(Comment.user)).order_by(desc(Comment.id)).limit(100)
    result = await session.execute(stmt)
    comments = result.scalars().all()
    return [
        CommentRead(
            id=c.id,
            content=c.content,
            user_id=c.user_id,
            article_id=c.article_id,
            parent_id=c.parent_id,
            created_at=c.created_at,
            username=c.user.username if c.user else None,
        )
        for c in comments
    ]

@router.get("/by_article/{article_id}", response_model=List[CommentRead])
async def list_comments_by_article(
    article_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User | None = Depends(current_active_user),  # 获取当前登录用户
):
    stmt = select(Comment).options(joinedload(Comment.user)).where(Comment.article_id == article_id).order_by(desc(Comment.id))
    result = await session.execute(stmt)
    comments = result.scalars().all()

    liked_comment_ids = set()
    if current_user:
        # 查询当前用户点赞的评论id集合
        stmt_likes = select(Like.comment_id).where(Like.user_id == current_user.id, Like.comment_id.in_([c.id for c in comments]))
        result_likes = await session.execute(stmt_likes)
        liked_comment_ids = set(row[0] for row in result_likes.all())

    # 根据 parent_id 分类
    comment_map = defaultdict(list)
    for comment in comments:
        comment_map[comment.parent_id].append(comment)

    # 构造树状结构
    def build_comment_tree(comment: Comment) -> CommentRead:
        return CommentRead(
            id=comment.id,
            content=comment.content,
            article_id=comment.article_id,
            user_id=comment.user_id,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            username=comment.user.username if comment.user else None,
            like_count=len(liked_comment_ids),
            liked=(comment.id in liked_comment_ids if current_user else False),
            replies=[build_comment_tree(child) for child in comment_map.get(comment.id, [])]
        )

    # 只返回一级评论（parent_id is None）
    root_comments = comment_map[None]
    return [build_comment_tree(c) for c in root_comments]