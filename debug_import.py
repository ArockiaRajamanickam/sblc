import traceback
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import app.main...")
    import app.main
    print("Success!")
except Exception:
    traceback.print_exc()
