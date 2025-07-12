import secrets
import hashlib
import base64
import aiohttp
from fastapi import HTTPException, status

from fastapi_application.core.config import settings
from datetime import datetime, timedelta
from jose import jwt
from fastapi_application.core.schemas.token_data import TokenData


def generate_code():
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode().replace("=", "")
    return code_challenge, code_verifier


def generate_state() -> str:
    return secrets.token_urlsafe(32)


async def exchange_code_for_token(code, device_id, state, code_verifier):
    async with aiohttp.ClientSession() as session:
        data = {
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
            "redirect_uri": settings.vk.redirect_uri,
            "code": code,
            "client_id": settings.vk.client_id,
            "device_id": device_id,
            "state": state,
        }
        async with session.post("https://id.vk.com/oauth2/auth", data=data) as response:
            if response.status != 200:
                error = await response.text()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
            return await response.json()


async def get_vk_data(access_token: str):
    async with aiohttp.ClientSession() as session:
        data = {
            "access_token": access_token,
            "client_id": settings.vk.client_id,
        }
        async with session.post("https://id.vk.com/oauth2/user_info", data=data) as response:
            if response.status != 200:
                error = await response.text()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
            data = await response.json()
            return data["user"]


async def generate_jwt(user_id: int, expire_delta: int = settings.jwt.expire_minutes):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now() + timedelta(expire_delta),
    }
    jwt_encode = jwt.encode(payload, settings.jwt.secret_key, settings.jwt.algorithm)
    return jwt_encode


async def verify_jwt(token: str, credentials_exception: Exception):
    try:
        jwt_decoded = jwt.decode(token, settings.jwt.secret_key, settings.jwt.algorithm)

        id = jwt_decoded.get("sub")
        print(id)
        token_data = TokenData(user_id=str(id))

    except:
        raise credentials_exception
    return token_data
