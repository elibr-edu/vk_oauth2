import secrets
import hashlib
import base64
import aiohttp
from fastapi import HTTPException, status
from fastapi_application.core.config import settings


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


async def get_vk_data(access_token: str, user_id: int):
    async with aiohttp.ClientSession() as session:
        params = {
            "access_token": access_token,
            "user_ids": user_id,
            "v": "5.199",
        }
        async with session.get("https://api.vk.com/method/users.get", params=params) as response:
            if response.status != 200:
                error = await response.text()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
            return await response.json()
