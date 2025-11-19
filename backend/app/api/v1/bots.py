# app/api/v1/bots.py
from typing import Any, List, Optional # 引入 Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel # 引入 BaseModel

from ...services import AIService
from ...models import User
from ..deps import get_current_active_user, check_student # 引入 check_student

router = APIRouter()

# --- 新增 Pydantic 模型 ---
class AIStatusResponse(BaseModel):
    is_initialized: bool

class AIPointsResponse(BaseModel):
    points: Optional[int] = None
    error: Optional[str] = None

# 定义默认头像URL，方便管理
DEFAULT_AVATAR_URL = "https://psc2.cf2.poecdn.net/assets/_next/static/media/defaultAvatar.7e5c73d2.png"

@router.get("/list", dependencies=[Depends(check_student)]) # 添加学生权限依赖
async def list_available_bots(
    current_user: User = Depends(get_current_active_user),
    count: int = Query(20, ge=1, le=100),
    get_all: bool = Query(False)
) -> List[dict]:
    """
    获取当前用户可用的Poe AI机器人列表。
    支持一次性获取指定数量或全量获取。
    """
    ai_service = AIService.get_instance(current_user.student.id)
    if not ai_service.is_available():
        raise HTTPException(
            status_code=400,
            detail="AI服务未初始化，请先配置token"
        )
    
    try:
        bots_data = await ai_service.poe_client.get_available_bots(count=count, get_all=get_all)
        
        formatted_bots = []
        for handle, data in bots_data.items():
            bot_info = data.get("bot", {})
            
            # --- 核心修复点 ---
            # 1. 安全地获取 picture 字典
            picture_info = bot_info.get("picture")
            
            # 2. 如果 picture 字典存在，则尝试获取 url，否则 url 为 None
            picture_url = picture_info.get("url") if picture_info else None
            
            # 3. 如果最终 picture_url 为空 (None 或空字符串)，则使用默认URL
            avatar_url = picture_url or DEFAULT_AVATAR_URL
            
            formatted_bots.append({
                "handle": bot_info.get("handle", ""),
                "displayName": bot_info.get("displayName", ""),
                "description": bot_info.get("description", ""),
                "avatarUrl": avatar_url, # 使用我们安全获取到的 URL
            })
        
        return formatted_bots
        
    except Exception as e:
        import traceback
        traceback.print_exc() # 在服务器端打印详细错误，方便调试
        raise HTTPException(
            status_code=500,
            detail=f"获取机器人列表失败: {str(e)}"
        )


# --- 新增端点 1: 查询AI服务状态 ---
@router.get("/status", response_model=AIStatusResponse, dependencies=[Depends(check_student)])
async def get_ai_status(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """检查当前用户的AI服务是否已初始化。"""
    ai_service = AIService.get_instance(current_user.student.id)
    return {"is_initialized": ai_service.is_available()}

# --- 新增端点 2: 查询Poe积分 ---
@router.get("/points", response_model=AIPointsResponse, dependencies=[Depends(check_student)])
async def get_poe_points(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取当前用户的Poe积分余额。"""
    ai_service = AIService.get_instance(current_user.student.id)
    info = await ai_service.get_account_info()
    if info:
        return {"points": info.get("message_points")}
    return {"points": None, "error": "无法获取积分，AI服务可能未初始化或配置错误。"}