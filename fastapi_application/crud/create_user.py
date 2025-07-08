from typing import Annotated

from fastapi import Depends
from fastapi_application.core.models import db_helper
from fastapi_application.core.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession


async def create_user(
    user_id: int,
    first_name: str,
    last_name: str,
    email: str,
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> User:
    user_profile = await db.get(User, user_id)
    if user_profile:
        return user_profile
    new_user = User(id=user_id, first_name=first_name, last_name=last_name, email=email)
    db.add(new_user)
    await db.commit()
    return new_user
