import uvicorn
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.main import app

if __name__ == "__main__":
    print("Starting MPLADS Sentinel AI backend server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
