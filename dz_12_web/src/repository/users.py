from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserResponse, UserModel


async def get_user_by_email(email: str, db: AsyncSession):
    sq = select(User).filter_by(email=email)
    result = await db.execute(sq)
    user = result.scalar_one_or_none()
    return user


async def create_user(body: UserModel, db: AsyncSession):
    user = User(**body.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user 


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    user.refresh_token = token
    await db.commit()
    await db.refresh(user)


async def update_user(body: UserResponse, db: AsyncSession, user: User):
    if body.name is not None:
        user.name = body.name
    if body.surname is not None:
        user.surname = body.surname
    if body.phone is not None:
        user.phone = body.phone
    if body.email is not None:
        user.email = body.email
        await db.commit()
        await db.refresh(user)
    return user


async def remove_user(user: User, db: AsyncSession):
    await db.delete(user)
    await db.commit()
    return user
