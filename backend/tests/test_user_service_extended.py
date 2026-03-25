
    async def test_get_user_statistics_new_user(self, db_session):
        """Test getting statistics for a new user"""
        service = UserService(db_session)
        email = "stats_new@example.com"
        await service.register(email, "Pass123", {})
        user = await service._get_user_by_email(email)
        
        stats = await service.get_user_statistics(user.user_id)
        assert stats.total_workouts == 0
        assert stats.total_reps == 0
        assert stats.average_form_score == 0.0
        assert stats.current_streak == 0

    async def test_notification_preferences_default(self, db_session):
        """Test default notification preferences"""
        service = UserService(db_session)
        email = "prefs@example.com"
        await service.register(email, "Pass123", {})
        user = await service._get_user_by_email(email)
        
        prefs = await service.get_notification_preferences(user.user_id)
        assert prefs.email_notifications is True
        assert prefs.push_notifications is True
        assert prefs.workout_residues is True

    async def test_update_notification_preferences(self, db_session):
        """Test updating notification preferences"""
        service = UserService(db_session)
        email = "prefs_update@example.com"
        await service.register(email, "Pass123", {})
        user = await service._get_user_by_email(email)
        
        from app.schemas.user import NotificationPreferencesUpdate
        updates = NotificationPreferencesUpdate(email_notifications=False)
        
        updated = await service.update_notification_preferences(user.user_id, updates)
        assert updated.email_notifications is False
        assert updated.push_notifications is True  # unchanged
