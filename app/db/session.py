from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 数据库“引擎”，负责连接数据库本体。
# 📌 用它来创建连接、执行建表、事务等底层操作。

engine = create_async_engine(DATABASE_URL)

# 会话工厂，帮你生成“数据库会话”对象，用于操作表数据。
# 📌 你可以从它生成 AsyncSession 来进行增删改查。

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# FastAPI 的依赖函数，用来在每个请求中获取一个独立的数据库会话。
# 📌 保证数据库操作的独立性、安全性和自动关闭。

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
