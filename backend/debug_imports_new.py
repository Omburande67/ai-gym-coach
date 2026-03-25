
try:
    print("Testing app.core.database...")
    from app.core.database import get_db
    print("SUCCESS: get_db imported")
except ImportError as e:
    print(f"FAILED: app.core.database import: {e}")

try:
    print("\nTesting app.schemas.user...")
    from app.schemas.user import Token, UserCreate, UserLogin, UserProfile
    print("SUCCESS: schemas imported")
except ImportError as e:
    print(f"FAILED: app.schemas.user import: {e}")

try:
    print("\nTesting app.services.user_service...")
    from app.services.user_service import UserService
    print("SUCCESS: UserService imported")
except ImportError as e:
    print(f"FAILED: app.services.user_service import: {e}")

try:
    print("\nTesting app.api.auth...")
    from app.api import auth
    print("SUCCESS: auth imported")
except ImportError as e:
    print(f"FAILED: app.api.auth import: {e}")
    import traceback
    traceback.print_exc()
