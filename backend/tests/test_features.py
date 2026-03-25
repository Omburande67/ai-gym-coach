
import pytest
from app.services.user_service import UserService
from app.schemas.workout import WorkoutSessionCreate, ExerciseRecordCreate, WorkoutPlanCreate
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_streak_calculation(db_session):
    """Test streak calculation logic."""
    service = UserService(db_session)
    email = "streak@example.com"
    await service.register(email, "Pass123", {})
    user = await service._get_user_by_email(email)
    user_id = user.user_id

    # Day 1
    session_data1 = WorkoutSessionCreate(
        user_id=user_id,
        start_time=datetime.now() - timedelta(days=2),
        end_time=datetime.now() - timedelta(days=2) + timedelta(minutes=30),
        exercise_records=[]
    )
    await service.save_workout(session_data1)
    
    stats = await service.get_user_statistics(user_id)
    assert stats.current_streak == 1

    # Day 2 (Consecutive)
    session_data2 = WorkoutSessionCreate(
        user_id=user_id,
        start_time=datetime.now() - timedelta(days=1),
        end_time=datetime.now() - timedelta(days=1) + timedelta(minutes=30),
        exercise_records=[]
    )
    
    # We need to manually call _update_streak or ensure save_workout calls it
    # save_workout calls it now.
    await service.save_workout(session_data2)

    stats = await service.get_user_statistics(user_id)
    assert stats.current_streak == 2

    # Day 4 (Missed Day 3) -> Reset
    session_data3 = WorkoutSessionCreate(
        user_id=user_id,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=30),
        exercise_records=[]
    )
    await service.save_workout(session_data3)

    stats = await service.get_user_statistics(user_id)
    assert stats.current_streak == 1 
    assert stats.longest_streak == 2

@pytest.mark.asyncio
async def test_workout_summary(db_session):
    """Test workout summary generation logic."""
    service = UserService(db_session)
    email = "summary@example.com"
    await service.register(email, "Pass123", {})
    user = await service._get_user_by_email(email)
    
    # Create session with mistakes
    record1 = ExerciseRecordCreate(
        exercise_type="squat",
        reps_completed=10,
        form_score=80.0,
        mistakes=[{"type": "knee_valgus", "suggestion": "Keep knees out"}]
    )
    record2 = ExerciseRecordCreate(
        exercise_type="squat",
        reps_completed=10,
        form_score=85.0,
        mistakes=[{"type": "knee_valgus", "suggestion": "Keep knees out"}]
    )
    
    session_data = WorkoutSessionCreate(
        user_id=user.user_id,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=10),
        exercise_records=[record1, record2]
    )
    
    saved_session = await service.save_workout(session_data)
    summary = await service.get_workout_summary(saved_session.session_id)
    
    assert summary["total_reps"] == 20
    assert summary["average_form_score"] == 82.5
    assert len(summary["top_mistakes"]) == 1
    assert summary["top_mistakes"][0]["type"] == "knee_valgus"
    assert summary["top_mistakes"][0]["count"] == 2
