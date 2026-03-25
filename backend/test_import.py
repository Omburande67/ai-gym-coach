import traceback
import sys
import os

sys.path.append(os.getcwd())

try:
    print("Testing import of app.main...")
    from app.main import app
    print("Import successful!")
except Exception:
    traceback.print_exc()
