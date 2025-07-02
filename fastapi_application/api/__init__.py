from fastapi import APIRouter
from fastapi_application.crud.oauth import router as oauth_router
from fastapi_application.core.config import settings

router = APIRouter(
    prefix=settings.api.prefix,
)

router.include_router(oauth_router)
