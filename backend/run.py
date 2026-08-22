import uvicorn
import os
import sys

# Ensure the parent directory is in the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    print("Starting MPLADS Sentinel AI backend server...")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
