"""Unit tests for UserService"""

import pytest
from uuid import uuid4

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import UserProfile


@pytest.mark.asyncio
class TestUserService:
    """Test suite for UserService"""

    async def test_register_new_user(self, db_session):
        """Test registering a new user"""
        service = UserService(db_session)
        
        email = "test@example.com"
        password = "TestPass123"
        profile_data = {
            "weight_kg": 70.5,
            "height_cm": 175.0,
            "body_type": "mesomorph",
            "fitness_goals": ["weight_loss", "muscle_gain"],
        }
        
        user_profile = await service.register(email, password, profile_data)
        
        assert user_profile.email == email
        assert user_profile.weight_kg == 70.5
        assert user_profile.height_cm == 175.0
        assert user_profile.body_type == "mesomorph"
        assert user_profile.fitness_goals == ["weight_loss", "muscle_gain"]
        assert user_profile.user_id is not None
        assert user_profile.created_at is not None

    async def test_register_duplicate_email(self, db_session):
        """Test registering with duplicate email raises error"""
        service = UserService(db_session)
        
        email = "duplicate@example.com"
        password = "TestPass123"
        profile_data = {}
        
        # Register first user
        await service.register(email, password, profile_data)
        
        # Attempt to register with same email
        with pytest.raises(ValueError, match="Email already registered"):
            await service.register(email, password, profile_data)

    async def test_authenticate_valid_credentials(self, db_session):
        """Test authentication with valid credentials"""
        service = UserService(db_session)
        
        email = "auth@example.com"
        password = "TestPass123"
        profile_data = {}
        
        # Register user
        await service.register(email, password, profile_data)
        
        # Authenticate
        token = await service.authenticate(email, password)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_authenticate_invalid_email(self, db_session):
        """Test authentication with non-existent email"""
        service = UserService(db_session)
        
        token = await service.authenticate("nonexistent@example.com", "TestPass123")
        
        assert token is None

    async def test_authenticate_invalid_password(self, db_session):
        """Test authentication with incorrect password"""
        service = UserService(db_session)
        
        email = "wrongpass@example.com"
        password = "TestPass123"
        profile_data = {}
        
        # Register user
        await service.register(email, password, profile_data)
        
        # Authenticate with wrong password
        token = await service.authenticate(email, "WrongPass456")
        
        assert token is None

    async def test_get_profile_existing_user(self, db_session):
        """Test retrieving profile for existing user"""
        service = UserService(db_session)
        
        email = "profile@example.com"
        password = "TestPass123"
        profile_data = {
            "weight_kg": 80.0,
            "height_cm": 180.0,
        }
        
        # Register user
        registered_user = await service.register(email, password, profile_data)
        
        # Get profile
        profile = await service.get_profile(registered_user.user_id)
        
        assert profile is not None
        assert profile.user_id == registered_user.user_id
        assert profile.email == email
        assert profile.weight_kg == 80.0
        assert profile.height_cm == 180.0

    async def test_get_profile_nonexistent_user(self, db_session):
        """Test retrieving profile for non-existent user"""
        service = UserService(db_session)
        
        # Try to get profile with random UUID
        profile = await service.get_profile(uuid4())
        
        assert profile is None

    async def test_update_profile_existing_user(self, db_session):
        """Test updating profile for existing user"""
        service = UserService(db_session)
        
        email = "update@example.com"
        password = "TestPass123"
        profile_data = {
            "weight_kg": 70.0,
            "height_cm": 170.0,
            "body_type": "ectomorph",
        }
        
        # Register user
        registered_user = await service.register(email, password, profile_data)
        
        # Update profile
        updates = {
            "weight_kg": 75.0,
            "height_cm": 175.0,
            "body_type": "mesomorph",
            "fitness_goals": ["endurance"],
        }
        updated_profile = await service.update_profile(registered_user.user_id, updates)
        
        assert updated_profile is not None
        assert updated_profile.weight_kg == 75.0
        assert updated_profile.height_cm == 175.0
        assert updated_profile.body_type == "mesomorph"
        assert updated_profile.fitness_goals == ["endurance"]

    async def test_update_profile_nonexistent_user(self, db_session):
        """Test updating profile for non-existent user"""
        service = UserService(db_session)
        
        updates = {"weight_kg": 75.0}
        updated_profile = await service.update_profile(uuid4(), updates)
        
        assert updated_profile is None

    async def test_password_hashing(self, db_session):
        """Test that passwords are properly hashed"""
        service = UserService(db_session)
        
        email = "hash@example.com"
        password = "TestPass123"
        profile_data = {}
        
        # Register user
        await service.register(email, password, profile_data)
        
        # Get user from database directly
        user = await service._get_user_by_email(email)
        
        # Verify password is hashed (not plaintext)
        assert user.password_hash != password
        assert len(user.password_hash) > 0
        
        # Verify password can be verified
        assert verify_password(password, user.password_hash)
