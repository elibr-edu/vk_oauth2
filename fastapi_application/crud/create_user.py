from typing import Annotated

from fastapi import Depends
from fastapi_application.core.models import db_helper
from fastapi_application.core.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession


async def create_user(
    id: int, first_name: str, last_name: str, db: Annotated[AsyncSession, Depends(db_helper.session_getter)]
) -> User:
    pass
