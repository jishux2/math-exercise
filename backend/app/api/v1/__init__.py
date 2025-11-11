from fastapi import APIRouter
from . import auth, users, exercises, agent

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])  # 新增