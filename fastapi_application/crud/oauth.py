from typing import Annotated

from sqlalchemy import select
from fastapi_application.core.models import db_helper
from fastapi_application.core.models.models import User
from fastapi_application.core.schemas.user_create import UserCreate
from fastapi_application.core.schemas.user_login import UserLogin
from fastapi_application.crud.verify_hashes import hash_password, verify_hashes
from fastapi_application.crud.generate_secrets import (
    exchange_code_for_token,
    generate_code,
    generate_state,
    get_vk_data,
    generate_jwt,
    verify_jwt,
)
from fastapi_application.crud.vk_create_user import vk_create_user
from fastapi_application.core.config import settings
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/vk/auth")
async def redirect_url():
    code_challenge, code_verifier = generate_code()
    state = generate_state()
    auth_url = (
        "https://id.vk.com/authorize?"
        f"response_type=code&"
        f"client_id={settings.vk.client_id}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256&"
        f"redirect_uri={settings.vk.redirect_uri}&"
        f"state={state}&"
        f"scope=email"
    )

    response = RedirectResponse(auth_url)

    response.set_cookie(key="vk_state", value=f"{state}:{code_verifier}", secure=False, max_age=300, httponly=True)

    return response


@router.get("/vk/auth/callback")
async def login_vk(
    code: str,
    state: str,
    device_id: str,
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    request: Request,
):
    cookie = request.cookies.get("vk_state")

    if not cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cookie is invalid")

    saved_state, code_verifier = cookie.split(":")

    if saved_state != state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")

    token = await exchange_code_for_token(code, device_id, state, code_verifier)

    access_token = token["access_token"]

    user_info = await get_vk_data(access_token=access_token)

    user_id, first_name, last_name, email = (
        int(user_info["user_id"]),
        user_info["first_name"],
        user_info["last_name"],
        user_info["email"],
    )

    user = await vk_create_user(user_id, first_name, last_name, email, db)

    jwt_token = await generate_jwt(user.id)

    response = RedirectResponse(url="/")
    response.set_cookie(
        key="auth_token",
        value=f"Bearer {jwt_token}",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.jwt.expire_minutes,
    )
    return response


@router.get("/users/me")
async def get_current_user(request: Request, db: AsyncSession = Depends(db_helper.session_getter)):
    cookie = request.cookies.get("auth_token")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not cookie:
        raise credentials_exception

    token = cookie.replace("Bearer", "").strip()

    token_data = await verify_jwt(token, credentials_exception)

    user_query = select(User).where(User.id == int(token_data.user_id))

    query_result = await db.scalars(user_query)

    user = query_result.first()

    return user


@router.post("/login")
async def user_login(credentials: UserLogin, db: Annotated[AsyncSession, Depends(db_helper.session_getter)]):
    user_query = select(User).where(User.email == credentials.email)
    query_result = await db.scalars(user_query)
    user = query_result.first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not found")
    if not verify_hashes(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad password")

    token = await generate_jwt(user.id)

    response = RedirectResponse(url="/")

    response.set_cookie(
        key="auth_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.jwt.expire_minutes,
    )
    return response


@router.post("/register")
async def register_user(credentials: UserCreate, db: Annotated[AsyncSession, Depends(db_helper.session_getter)]):
    user_query = select(User).where(User.email == credentials.email)
    query_result = await db.scalars(user_query)
    user = query_result.first()

    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User exist already!")

    user_data = credentials.model_dump(exclude={"password"})
    user_data["password"] = hash_password(credentials.password)
    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    return new_user
