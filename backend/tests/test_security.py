"""Unit tests for security utilities"""

from uuid import uuid4

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    """Test password hashing with bcrypt"""
    password = "TestPassword123"
    
    # Hash the password
    hashed = hash_password(password)
    
    # Verify hash is not plaintext
    assert hashed != password
    assert len(hashed) > 0
    
    # Verify password can be verified
    assert verify_password(password, hashed) is True
    
    # Verify wrong password fails
    assert verify_password("WrongPassword", hashed) is False


def test_password_hash_uniqueness():
    """Test that same password produces different hashes (salt)"""
    password = "TestPassword123"
    
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    # Hashes should be different due to salt
    assert hash1 != hash2
    
    # But both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_jwt_token_creation():
    """Test JWT token creation"""
    user_id = uuid4()
    email = "test@example.com"
    
    token = create_access_token({"user_id": user_id, "email": email})
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_jwt_token_decode():
    """Test JWT token decoding"""
    user_id = uuid4()
    email = "test@example.com"
    
    # Create token
    token = create_access_token({"user_id": user_id, "email": email})
    
    # Decode token
    payload = decode_access_token(token)
    
    assert payload is not None
    assert payload["user_id"] == str(user_id)  # UUID converted to string
    assert payload["email"] == email
    assert "exp" in payload  # Expiration time should be present


def test_jwt_token_invalid():
    """Test decoding invalid JWT token"""
    invalid_token = "invalid.token.here"
    
    payload = decode_access_token(invalid_token)
    
    assert payload is None
