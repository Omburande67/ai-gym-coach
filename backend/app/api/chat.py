from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserProfile
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.user_service import UserService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the AI coach and get a response.
    
    Implements Requirements 8.1, 8.2:
    - Receive user message
    - Build context
    - Get AI response
    """
    user_service = UserService(db)
    llm_service = LLMService()
    
    # Gather user context
    user_profile_dict = {
        "username": current_user.email,
        "fitness_goals": ", ".join(current_user.fitness_goals) if current_user.fitness_goals else "General Fitness",
        "body_type": current_user.body_type,
        "weight_kg": current_user.weight_kg,
        "height_cm": current_user.height_cm,
    }
    
    # Get last workout
    history = await user_service.get_workout_history(current_user.user_id, limit=1)
    last_workout_str = "None yet"
    if history:
        w = history[0]
        if w.start_time:
             last_workout_str = f"{w.start_time.date()} - {w.total_reps} reps"
             
    # Get streak (mock for now)
    streak = 0
    # In Task 15 we will implement streak tracking properly.
    
    user_context = {
        "last_workout": last_workout_str,
        "streak": streak
    }
    
    # Convert request.history to list of dicts
    chat_history = []
    if request.history:
        for msg in request.history:
            chat_history.append({"role": msg.role, "content": msg.content})
            
    response_text = await llm_service.chat(
        user_profile_dict,
        user_context,
        request.message,
        chat_history
    )
    
    return ChatResponse(response=response_text)
