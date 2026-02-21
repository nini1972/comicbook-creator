#!/usr/bin/env python
"""Ultra-minimal test"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Starting test...")
from src.visual_comic_crew.tools.orchestrator_tools import StatusTrackerTool
print("SUCCESS: Imported StatusTrackerTool")
tracker = StatusTrackerTool()
print("SUCCESS: Created instance")
