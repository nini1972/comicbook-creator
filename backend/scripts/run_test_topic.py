"""Runner to start a test run using the TEST_TOPIC object.
This script will set a safe dummy API key (if none provided), load the VisualComicCrew
and kickoff the crew with the test topic. It avoids calling real paid LLMs by
setting a small dummy environment variable; change as needed.
"""
import os
from pathlib import Path
import time
import sys
# file: backend/scripts/run_test_topic.py
# Resolve repository and backend paths reliably
REPO_ROOT = Path(__file__).resolve().parents[2]   # e.g. .../comicbook
BACKEND_DIR = REPO_ROOT / "backend"
BACKEND_SRC = BACKEND_DIR / "src"# file: backend/scripts/run_test_topic.py

# Make both backend and backend/src importable regardless of CWD
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_SRC))

# Load test object
from importlib import util as _util
test_topic_path = BACKEND_DIR / 'scripts' / 'test_topic.py'
spec = _util.spec_from_file_location('test_topic', str(test_topic_path))
test_topic_mod = _util.module_from_spec(spec)
spec.loader.exec_module(test_topic_mod)
TEST_TOPIC = getattr(test_topic_mod, 'TEST_TOPIC')

# Simple safeguard: set a dummy key if no LLM key found so crew will attempt to run in local/mock mode
for k in ("OPENAI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY", "GENAI_API_KEY", "LITELLM_API_KEY"):
    if not os.getenv(k):
        os.environ[k] = "DUMMY_KEY_FOR_LOCAL_TEST"

print("DEBUG: Using masked test keys (DUMMY_KEY_FOR_LOCAL_TEST) to avoid hitting real APIs")

# Run the crew in a restricted mode
from visual_comic_crew.run_crew import run

# Replace input flow: monkeypatch get_topic to return our test topic title
import visual_comic_crew.run_crew as rc
rc.get_topic = lambda: TEST_TOPIC['title']

print("DEBUG: Starting crew run with TEST_TOPIC")
run()
