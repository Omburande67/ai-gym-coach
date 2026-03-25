"""User management API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas.user import TokenData, UserProfile, UserUpdate, UserStatistics, NotificationPreferencesResponse, NotificationPreferencesUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """
    Get current user's profile.
    """
    user_service = UserService(db)
    
    user_profile = await user_service.get_profile(current_user.user_id)
    
    if user_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user_profile


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    updates: UserUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """
    Update current user's profile.
    """
    user_service = UserService(db)
    
    # Convert Pydantic model to dict, excluding unset fields
    update_data = updates.model_dump(exclude_unset=True)
    
    user_profile = await user_service.update_profile(
        user_id=current_user.user_id,
        updates=update_data,
    )
    
    if user_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user_profile

@router.get("/statistics", response_model=UserStatistics)
async def get_user_statistics(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserStatistics:
    """Get summarized user statistics and streak."""
    user_service = UserService(db)
    return await user_service.get_user_statistics(current_user.user_id)

@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_preferences(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationPreferencesResponse:
    """Get notification preferences."""
    user_service = UserService(db)
    return await user_service.get_notification_preferences(current_user.user_id)

@router.put("/preferences", response_model=NotificationPreferencesResponse)
async def update_preferences(
    updates: NotificationPreferencesUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationPreferencesResponse:
    """Update notification preferences."""
    user_service = UserService(db)
    return await user_service.update_notification_preferences(current_user.user_id, updates)
