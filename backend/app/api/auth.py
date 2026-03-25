"""Authentication API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import Token, UserCreate, UserLogin, UserProfile
from app.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """
    Register a new user account.
    
    Args:
        user_data: User registration data including email, password, and profile info
        db: Database session
        
    Returns:
        UserProfile: Created user profile
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    user_service = UserService(db)
    
    try:
        profile_data = {
            "weight_kg": user_data.weight_kg,
            "height_cm": user_data.height_cm,
            "body_type": user_data.body_type,
            "fitness_goals": user_data.fitness_goals,
        }
        
        user_profile = await user_service.register(
            email=user_data.email,
            password=user_data.password,
            profile_data=profile_data,
        )
        
        return user_profile
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Authenticate user and return JWT access token.
    
    Args:
        credentials: User login credentials (email and password)
        db: Database session
        
    Returns:
        Token: JWT access token
        
    Raises:
        HTTPException: If authentication fails
    """
    user_service = UserService(db)
    
    access_token = await user_service.authenticate(
        email=credentials.email,
        password=credentials.password,
    )
    
    if access_token is None:
        # Debug logging for the user to understand why it failed
        # In a real production app, we wouldn't distinguish between email/password failure to prevent enumeration
        user = await user_service._get_user_by_email(credentials.email)
        if not user:
            print(f"AUTH FAILURE: User not found with email {credentials.email}")
        else:
            print(f"AUTH FAILURE: Password mismatch for user {credentials.email}")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return Token(access_token=access_token)
