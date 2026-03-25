import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.services.user_service import UserService
import bcrypt

async def debug_login():
    async with AsyncSessionLocal() as db:
        user_service = UserService(db)
        email = "test@example.com"
        
        # Manually check user
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"User {email} not found in DB")
            return
            
        print(f"User {email} found.")
        print(f"Hash in DB: {user.password_hash}")
        
        # Test a known password if we knew it... 
        # But we don't. Let's try hashing 'Password123' and comparing.
        test_pass = "Password123"
        is_match = bcrypt.checkpw(test_pass.encode('utf-8'), user.password_hash.encode('utf-8'))
        print(f"Match with 'Password123': {is_match}")
        
        # Try authenticate service
        token = await user_service.authenticate(email, test_pass)
        print(f"Service authenticate result: {'Success' if token else 'Failed'}")

if __name__ == "__main__":
    asyncio.run(debug_login())
