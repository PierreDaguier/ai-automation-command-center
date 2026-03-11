import os
import sys
from pathlib import Path
from uuid import uuid4

os.environ["DATABASE_URL"] = f"sqlite:///./test_{uuid4().hex}.db"
os.environ["ENABLE_METRICS"] = "false"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
