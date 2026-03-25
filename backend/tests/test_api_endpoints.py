"""Tests for user management API endpoints"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.main import app
from app.services.user_service import UserService


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency to use test database"""
    async def _override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_client(override_get_db) -> TestClient:
    """Create a test client with database override"""
    return TestClient(app)


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""
    
    def test_register_valid_user(self, test_client: TestClient) -> None:
        """Test registration with valid user data"""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "weight_kg": 70.5,
            "height_cm": 175.0,
            "body_type": "mesomorph",
            "fitness_goals": ["lose_weight", "build_muscle"],
        }
        
        response = test_client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["weight_kg"] == user_data["weight_kg"]
        assert data["height_cm"] == user_data["height_cm"]
        assert data["body_type"] == user_data["body_type"]
        assert data["fitness_goals"] == user_data["fitness_goals"]
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "password" not in data
        assert "password_hash" not in data
    
    def test_register_duplicate_email(self, test_client: TestClient) -> None:
        """Test registration with duplicate email fails"""
        user_data = {
            "email": "duplicate@example.com",
            "password": "SecurePass123",
            "weight_kg": 70.5,
            "height_cm": 175.0,
        }
        
        # Register first user
        response1 = test_client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Try to register with same email
        response2 = test_client.post("/api/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()
    
    def test_register_invalid_email(self, test_client: TestClient) -> None:
        """Test registration with invalid email format fails"""
        user_data = {
            "email": "not-an-email",
            "password": "SecurePass123",
        }
        
        response = test_client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_weak_password(self, test_client: TestClient) -> None:
        """Test registration with weak password fails"""
        # Password too short
        user_data = {
            "email": "test@example.com",
            "password": "Short1",
        }
        response = test_client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422
        
        # Password without uppercase
        user_data["password"] = "lowercase123"
        response = test_client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422
        
        # Password without lowercase
        user_data["password"] = "UPPERCASE123"
        response = test_client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422
        
        # Password without number
        user_data["password"] = "NoNumbers"
        response = test_client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_register_invalid_body_type(self, test_client: TestClient) -> None:
        """Test registration with invalid body type fails"""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "body_type": "invalid_type",
        }
        
        response = test_client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_register_minimal_data(self, test_client: TestClient) -> None:
        """Test registration with only required fields"""
        user_data = {
            "email": "minimal@example.com",
            "password": "SecurePass123",
        }
        
        response = test_client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["weight_kg"] is None
        assert data["height_cm"] is None
        assert data["body_type"] is None
        assert data["fitness_goals"] is None
    
    def test_login_valid_credentials(self, test_client: TestClient) -> None:
        """Test login with valid credentials returns token"""
        # Register user first
        register_data = {
            "email": "login@example.com",
            "password": "SecurePass123",
        }
        test_client.post("/api/auth/register", json=register_data)
        
        # Login
        login_data = {
            "email": "login@example.com",
            "password": "SecurePass123",
        }
        response = test_client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_email(self, test_client: TestClient) -> None:
        """Test login with non-existent email fails"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SecurePass123",
        }
        
        response = test_client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_invalid_password(self, test_client: TestClient) -> None:
        """Test login with incorrect password fails"""
        # Register user first
        register_data = {
            "email": "wrongpass@example.com",
            "password": "SecurePass123",
        }
        test_client.post("/api/auth/register", json=register_data)
        
        # Try to login with wrong password
        login_data = {
            "email": "wrongpass@example.com",
            "password": "WrongPassword123",
        }
        response = test_client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()


class TestUserEndpoints:
    """Test suite for user management endpoints"""
    
    def _register_and_login(self, test_client: TestClient) -> str:
        """Helper method to register and login a user, returning access token"""
        register_data = {
            "email": "user@example.com",
            "password": "SecurePass123",
            "weight_kg": 75.0,
            "height_cm": 180.0,
            "body_type": "mesomorph",
            "fitness_goals": ["build_muscle"],
        }
        test_client.post("/api/auth/register", json=register_data)
        
        login_data = {
            "email": "user@example.com",
            "password": "SecurePass123",
        }
        response = test_client.post("/api/auth/login", json=login_data)
        return response.json()["access_token"]
    
    def test_get_profile_authenticated(self, test_client: TestClient) -> None:
        """Test getting profile with valid authentication"""
        token = self._register_and_login(test_client)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/api/users/profile", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user@example.com"
        assert data["weight_kg"] == 75.0
        assert data["height_cm"] == 180.0
        assert data["body_type"] == "mesomorph"
        assert data["fitness_goals"] == ["build_muscle"]
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_get_profile_unauthenticated(self, test_client: TestClient) -> None:
        """Test getting profile without authentication fails"""
        response = test_client.get("/api/users/profile")
        assert response.status_code == 403  # No credentials provided
    
    def test_get_profile_invalid_token(self, test_client: TestClient) -> None:
        """Test getting profile with invalid token fails"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = test_client.get("/api/users/profile", headers=headers)
        assert response.status_code == 401
    
    def test_update_profile_authenticated(self, test_client: TestClient) -> None:
        """Test updating profile with valid authentication"""
        token = self._register_and_login(test_client)
        
        update_data = {
            "weight_kg": 80.0,
            "height_cm": 182.0,
            "body_type": "endomorph",
            "fitness_goals": ["lose_weight", "improve_endurance"],
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.put("/api/users/profile", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["weight_kg"] == 80.0
        assert data["height_cm"] == 182.0
        assert data["body_type"] == "endomorph"
        assert data["fitness_goals"] == ["lose_weight", "improve_endurance"]
        assert data["email"] == "user@example.com"  # Email unchanged
    
    def test_update_profile_partial(self, test_client: TestClient) -> None:
        """Test updating only some profile fields"""
        token = self._register_and_login(test_client)
        
        # Update only weight
        update_data = {"weight_kg": 78.0}
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.put("/api/users/profile", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["weight_kg"] == 78.0
        assert data["height_cm"] == 180.0  # Unchanged
        assert data["body_type"] == "mesomorph"  # Unchanged
    
    def test_update_profile_unauthenticated(self, test_client: TestClient) -> None:
        """Test updating profile without authentication fails"""
        update_data = {"weight_kg": 80.0}
        response = test_client.put("/api/users/profile", json=update_data)
        assert response.status_code == 403
    
    def test_update_profile_invalid_body_type(self, test_client: TestClient) -> None:
        """Test updating profile with invalid body type fails"""
        token = self._register_and_login(test_client)
        
        update_data = {"body_type": "invalid_type"}
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.put("/api/users/profile", json=update_data, headers=headers)
        
        assert response.status_code == 422
    
    def test_update_profile_invalid_weight(self, test_client: TestClient) -> None:
        """Test updating profile with invalid weight fails"""
        token = self._register_and_login(test_client)
        
        # Negative weight
        update_data = {"weight_kg": -10.0}
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.put("/api/users/profile", json=update_data, headers=headers)
        
        assert response.status_code == 422
    
    def test_update_profile_invalid_height(self, test_client: TestClient) -> None:
        """Test updating profile with invalid height fails"""
        token = self._register_and_login(test_client)
        
        # Zero height
        update_data = {"height_cm": 0}
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.put("/api/users/profile", json=update_data, headers=headers)
        
        assert response.status_code == 422


class TestEndToEndFlow:
    """Test complete user flow from registration to profile management"""
    
    def test_complete_user_flow(self, test_client: TestClient) -> None:
        """Test complete flow: register -> login -> get profile -> update profile"""
        # 1. Register
        register_data = {
            "email": "flow@example.com",
            "password": "SecurePass123",
            "weight_kg": 70.0,
            "height_cm": 175.0,
            "body_type": "ectomorph",
            "fitness_goals": ["build_muscle"],
        }
        register_response = test_client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201
        user_id = register_response.json()["user_id"]
        
        # 2. Login
        login_data = {
            "email": "flow@example.com",
            "password": "SecurePass123",
        }
        login_response = test_client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Get profile
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = test_client.get("/api/users/profile", headers=headers)
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["user_id"] == user_id
        assert profile_data["email"] == "flow@example.com"
        assert profile_data["weight_kg"] == 70.0
        
        # 4. Update profile
        update_data = {
            "weight_kg": 72.0,
            "fitness_goals": ["build_muscle", "improve_endurance"],
        }
        update_response = test_client.put(
            "/api/users/profile", json=update_data, headers=headers
        )
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["weight_kg"] == 72.0
        assert updated_data["fitness_goals"] == ["build_muscle", "improve_endurance"]
        
        # 5. Verify update persisted
        profile_response2 = test_client.get("/api/users/profile", headers=headers)
        assert profile_response2.status_code == 200
        final_data = profile_response2.json()
        assert final_data["weight_kg"] == 72.0
        assert final_data["fitness_goals"] == ["build_muscle", "improve_endurance"]
