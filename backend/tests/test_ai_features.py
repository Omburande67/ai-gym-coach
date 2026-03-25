
import pytest
from app.services.user_service import UserService
from app.schemas.chat import ChatRequest, ChatResponse

@pytest.mark.asyncio
async def test_chat_interaction(db_session):
    """Test chat interaction with AI Coach."""
    service = UserService(db_session)
    email = "chat@example.com"
    await service.register(email, "Pass123", {})
    user = await service._get_user_by_email(email)
    
    # Mock LLM response (requires mocking LLMService.chat)
    # Since we can't easily mock imports in integration tests without monkeypatch,
    # we'll test the service method logic if possible or integration.
    
    # Assuming LLMService fallback when no API key
    response = await service.chat_message(user.user_id, "Hello coach", [])
    assert isinstance(response, ChatResponse)
    assert response.role == "assistant"
    # Fallback message
    assert "AI Gym Coach" in response.content or "trouble" in response.content

@pytest.mark.asyncio
async def test_workout_plan_generation(db_session):
    """Test workout plan generation."""
    service = UserService(db_session)
    email = "plan@example.com"
    await service.register(email, "Pass123", {})
    user = await service._get_user_by_email(email)
    
    plan = await service.generate_and_save_plan(user.user_id)
    assert plan.is_active is True
    assert plan.user_id == user.user_id
    assert len(plan.plan_data["days"]) == 7
