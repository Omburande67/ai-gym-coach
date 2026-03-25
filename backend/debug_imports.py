try:
    print("Importing app.schemas.user...")
    from app.schemas.user import UserStatistics
    print("Success: UserStatistics imported.")
except ImportError as e:
    print(f"Failed to import UserStatistics: {e}")

try:
    print("Importing app.services.user_service...")
    from app.services.user_service import UserService
    print("Success: UserService imported.")
    print("UserService attributes:", dir(UserService))
except ImportError as e:
    print(f"Failed to import UserService: {e}")

try:
    print("Importing app.api.auth...")
    from app.api import auth
    print("Success: app.api.auth imported.")
except ImportError as e:
    print(f"Failed to import app.api.auth: {e}")

try:
    print("Importing app.main...")
    from app.main import app
    print("Success: app.main imported.")
except ImportError as e:
    print(f"Failed to import app.main: {e}")
