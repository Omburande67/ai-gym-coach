
import pytest
from app.services.user_service import UserService
from app.schemas.workout import WorkoutSessionCreate, ExerciseRecordCreate
from app.schemas.user import NotificationPreferencesUpdate

@pytest.mark.asyncio
async def test_api_workflow(db_session):
    """
    Test full user workflow:
    1. Register
    2. Get Profile
    3. Update Profile
    4. Save Workout
    5. Get Summary
    6. Generate Plan
    7. Chat with Coach
    8. Check Notifications
    """
    service = UserService(db_session)
    
    # 1. Register
    email = "workflow2@example.com"
    await service.register(email, "Pass123", {"weight_kg": 70})
    user = await service._get_user_by_email(email)
    assert user is not None
    user_id = user.user_id

    # 2. Get Profile
    profile = await service.get_profile(user_id)
    assert profile.email == email
    
    # 3. Update Profile
    updates = {"fitness_goals": ["strength"]}
    updated_profile = await service.update_profile(user_id, updates)
    assert updated_profile.fitness_goals == ["strength"]
    
    # 4. Save Workout
    from datetime import datetime
    session_data = WorkoutSessionCreate(
        user_id=user_id,
        start_time=datetime.now(),
        end_time=datetime.now(),
        exercise_records=[
            ExerciseRecordCreate(exercise_type="squat", reps_completed=10, form_score=90.0)
        ]
    )
    saved_session = await service.save_workout(session_data)
    
    # 5. Get Summary
    summary = await service.get_workout_summary(saved_session.session_id)
    assert summary["total_reps"] == 10
    
    # 6. Generate Plan (Mock LLM inside service if possible, or verify structure)
    # Check if plan generation works (mocked or real without API key)
    plan = await service.generate_and_save_plan(user_id)
    assert plan.is_active is True
    
    # 7. Chat
    chat_resp = await service.chat_message(user_id, "hi", [])
    assert chat_resp is not None
    
    # 8. Check Notifications Preferences
    prefs = await service.get_notification_preferences(user_id)
    assert prefs.email_notifications is True
    
    # Update Prefs
    await service.update_notification_preferences(
        user_id, 
        NotificationPreferencesUpdate(email_notifications=False)
    )
    prefs_updated = await service.get_notification_preferences(user_id)
    assert prefs_updated.email_notifications is False

    # Check Stats
    stats = await service.get_user_statistics(user_id)
    assert stats.total_workouts == 1
    assert stats.current_streak == 1
