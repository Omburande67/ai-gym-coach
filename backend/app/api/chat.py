"""Chat API endpoints for AI Coach"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List

from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = None
    context: Optional[dict] = None


@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Process chat messages and return AI coach responses.
    """
    # Get user info safely
    fitness_goals = current_user.fitness_goals if current_user.fitness_goals else ["General Fitness"]
    user_name = current_user.email.split('@')[0] if current_user.email else "Athlete"
    
    # Simple response based on message content
    message_lower = request.message.lower()
    
    if any(word in message_lower for word in ["push", "pushup", "push-up"]):
        response = "💪 For push-ups: Keep your back straight, elbows at 45°, and lower until chest is 2 inches from ground. Breathe in on the way down, out on the way up!"
        suggestions = ["Engage your core", "Don't let hips sag", "Full range of motion"]
    
    elif any(word in message_lower for word in ["squat", "squats"]):
        response = "🏋️ For squats: Keep chest up, knees tracking over toes, go as low as comfortable (thighs parallel to ground). Maintain neutral spine throughout."
        suggestions = ["Keep weight in heels", "Don't round your back", "Go deep but comfortable"]
    
    elif any(word in message_lower for word in ["plank"]):
        response = "🔥 For plank: Keep body in straight line from head to heels, engage core, don't let hips sag or pike up. Hold steady and breathe!"
        suggestions = ["Squeeze glutes", "Look slightly forward", "Don't hold breath"]
    
    elif any(word in message_lower for word in ["jumping", "jack"]):
        response = "⭐ For jumping jacks: Land softly, keep arms straight overhead, engage core, breathe rhythmically. Start slow, build speed gradually."
        suggestions = ["Land softly", "Full arm extension", "Maintain rhythm"]
    
    elif any(word in message_lower for word in ["motivation", "motivate", "keep going"]):
        response = f"🔥 You've got this, {user_name}! Every rep makes you stronger. Consistency is key. Keep showing up and pushing your limits!"
        suggestions = ["You're doing great!", "One more rep!", "Stay focused!"]
    
    else:
        response = f"💪 Great question, {user_name}! Focus on proper form over speed. Your fitness goals: {', '.join(fitness_goals)}. Keep up the consistent work!"
        suggestions = ["Stay hydrated", "Breathe properly", "Listen to your body"]
    
    return ChatResponse(
        response=response,
        suggestions=suggestions,
        context={"user_goals": fitness_goals}
    )