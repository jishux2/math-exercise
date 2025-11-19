from fastapi import APIRouter
from . import auth, users, exercises, admin, messages, agent, bots # 1. 导入 bots

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(messages.router, tags=["messages"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])  # 新增
api_router.include_router(bots.router, prefix="/bots", tags=["bots"]) # 2. 注册新路由