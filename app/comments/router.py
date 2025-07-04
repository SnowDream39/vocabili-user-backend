# comments/api.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from sqlalchemy import desc, func
from typing import List
from collections import defaultdict

from app.db.session import get_async_session
from app.users.manager import current_active_user, current_active_user_optional, current_super_user
from app.db.models import Comment, User, Like
from .schemas import CommentCreate, CommentRead
from datetime import datetime, timezone

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("", response_model=CommentRead)
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


@router.get("/by_article/{article_id}", response_model=List[CommentRead])
async def list_comments_by_article(
    article_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User | None = Depends(current_active_user_optional),  # 获取当前登录用户
):
    stmt = select(Comment).options(joinedload(Comment.user)).where(Comment.article_id == article_id).order_by(desc(Comment.id))
    result = await session.execute(stmt)
    comments = result.scalars().all()

    comment_ids = [c.id for c in comments]

    # 查询每条评论的点赞数
    stmt_like_counts = (
        select(Like.comment_id, func.count().label("count"))
        .where(Like.comment_id.in_(comment_ids))
        .group_by(Like.comment_id)
    )
    result_counts = await session.execute(stmt_like_counts)
    like_counts = {row[0]: row[1] for row in result_counts.all()}


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
            liked=(comment.id in liked_comment_ids if current_user else False),
            like_count=like_counts.get(comment.id, 0),
            replies=[build_comment_tree(child) for child in comment_map.get(comment.id, [])]
        )

    # 只返回一级评论（parent_id is None）
    root_comments = comment_map[None]
    return [build_comment_tree(c) for c in root_comments]

# 管理员专用

@router.get("/all", response_model=List[CommentRead])
async def list_comments(
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_super_user)
    ):
    stmt = (
        select(Comment)
        .options(joinedload(Comment.user))
        .order_by(desc(Comment.id))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
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

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_super_user),
):
    result = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    await session.delete(comment)
    await session.commit()