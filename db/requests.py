from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db.tables import User, Group
from config.config import load_config
from sqlalchemy import select

db_config = load_config()

engine = create_async_engine(url=db_config.postgres.url)

AsyncSessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def create_user(telegram_id: int, first_name: str, last_name: str | None = None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
        if result.scalar_one_or_none() is None:
            user = User(telegram_id=telegram_id, first_name=first_name, last_name=last_name)
            session.add(user)
            await session.commit()

async def create_group(id: int, name: str, owner_id: int):
    async with AsyncSessionLocal() as session:
        group = Group(id=id, name=name, owner_id=owner_id)
        session.add(group)
        await session.commit()

async def set_user_language(user_id: int, language: str):
    stmt = select(User).where(User.telegram_id == user_id)
    async with AsyncSessionLocal() as session:
        user = await session.execute(stmt)
        user = user.scalar()
        user.language = language
        await session.commit()



