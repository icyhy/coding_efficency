from fastapi import APIRouter

from .auth import router as auth_router
from .repositories import router as repositories_router
from .analytics import router as analytics_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(repositories_router, prefix="/repositories", tags=["repositories"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])