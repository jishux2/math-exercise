from fastapi import Body  # 添加这行
import json  # 添加这行
from ...schemas.exercise import ExerciseResponse  # 添加这行
from sqlalchemy.orm import joinedload

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...database import get_db
from ...services import ExerciseService, AIService
from ...schemas import exercise as schemas
from ...models import User, Exercise, Question
from ..deps import get_current_active_user

from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/", response_model=schemas.ExerciseResponse)
def create_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_in: schemas.ExerciseCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    exercise_service = ExerciseService(db)
    return exercise_service.create_exercise(
        user_id=current_user.id,
        exercise_in=exercise_in
    )

@router.get("/", response_model=schemas.ExerciseListResponse)
def list_exercises(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
) -> Any:
    exercise_service = ExerciseService(db)
    exercises, total = exercise_service.get_user_exercises(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return {
        "exercises": exercises,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }

@router.get("/list", response_model=schemas.ExerciseListResponse)
async def list_exercises(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取用户的练习列表"""
    exercise_service = ExerciseService(db)
    exercises, total = exercise_service.get_user_exercises(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return {
        "exercises": [exercise.to_response() for exercise in exercises],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }

@router.get("/stats")
def get_user_exercise_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取用户的练习统计信息"""
    # 基础统计
    stats = db.query(
        func.count(Exercise.id).label('total_exercises'),
        func.count(Exercise.completed_at).label('completed_exercises'),
        func.avg(Exercise.final_score).label('average_score')
    ).filter(Exercise.user_id == current_user.id).first()

    # 正确率统计
    correct_answers = db.query(func.count(Question.id)).join(Exercise).filter(
        Exercise.user_id == current_user.id,
        Question.is_correct == True  # 使用hybrid_property
    ).scalar()
    
    total_questions = db.query(func.count(Question.id)).join(Exercise).filter(
        Exercise.user_id == current_user.id
    ).scalar()

    # 获取最近的练习分数历史
    score_history = db.query(
        Exercise.completed_at,
        Exercise.final_score
    ).filter(
        Exercise.user_id == current_user.id,
        Exercise.completed_at.isnot(None)
    ).order_by(Exercise.completed_at.desc()).limit(10).all()

    return {
        "total_exercises": stats[0] or 0,
        "completed_exercises": stats[1] or 0,
        "average_score": round(stats[2] or 0, 2),
        "accuracy_rate": round(
            (correct_answers / total_questions * 100) if total_questions else 0, 
            2
        ),
        "score_history": [
            {
                "date": completed_at.strftime("%m/%d"),
                "score": score
            }
            for completed_at, score in score_history
        ]
    }

@router.get("/{exercise_id}", response_model=schemas.ExerciseResponse)
def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    exercise_service = ExerciseService(db)
    exercise = exercise_service.get_exercise_with_questions(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if exercise.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return exercise

@router.post("/{exercise_id}/questions/{question_id}/answer")
def submit_answer(
    exercise_id: int,
    question_id: int,
    *,
    db: Session = Depends(get_db),
    answer_in: schemas.QuestionUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    exercise_service = ExerciseService(db)
    exercise = exercise_service.get(exercise_id)
    if not exercise or exercise.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    return exercise_service.submit_answer(
        exercise_id=exercise_id,
        question_id=question_id,
        user_answer=answer_in.user_answer,
        time_spent=answer_in.time_spent
    )

@router.post("/{exercise_id}/complete")
def complete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    exercise_service = ExerciseService(db)
    exercise = exercise_service.get(exercise_id)
    if not exercise or exercise.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    return {
        "final_score": exercise_service.complete_exercise(exercise_id)
    }

@router.get("/{exercise_id}/stats")
def get_exercise_stats(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    exercise_service = ExerciseService(db)
    exercise = exercise_service.get(exercise_id)
    if not exercise or exercise.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    return exercise_service.get_exercise_stats(exercise_id)

@router.post("/ai/initialize")
def initialize_ai(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tokens: dict = Body(...),
) -> Any:
    """初始化AI服务"""
    # 获取用户专属的AI服务实例
    ai_service = AIService.get_instance(current_user.id)
    success = ai_service.initialize_client(
        tokens.get("pb_token"),
        tokens.get("plat_token")
    )
    return {"success": success}

@router.get("/{exercise_id}/ai-feedback")
async def get_ai_feedback(
    exercise_id: int,
    feedback_type: str = Query("detailed", regex="^(detailed|summary)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取AI反馈（流式响应）"""
    from fastapi.responses import StreamingResponse

    # 获取用户专属的AI服务实例
    ai_service = AIService.get_instance(current_user.id)
    exercise_service = ExerciseService(db)
    # 使用joinedload预加载questions关系
    exercise = db.query(Exercise).options(
        joinedload(Exercise.questions)
    ).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if exercise.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 使用全局ai_service实例
    if not ai_service.is_available():
        return JSONResponse(
            status_code=400,
            content={"error": "AI服务未初始化，请先配置token"}
        )

    async def generate():
        # 手动创建ExerciseResponse对象，避免使用from_orm
        exercise_response = ExerciseResponse.model_validate(exercise)
        
        for chunk in ai_service.generate_feedback_stream(
            exercise_response,
            feedback_type
        ):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.post("/{exercise_id}/ai-feedback/stop")
def stop_ai_feedback(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """停止AI反馈生成"""
    exercise_service = ExerciseService(db)
    exercise = exercise_service.get(exercise_id)
    if not exercise or exercise.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Exercise not found")

    ai_service = AIService.get_instance(current_user.id)
    ai_service.stop_generation()
    return {"success": True}
