#!/usr/bin/env python
"""Test individual imports"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("1. Testing registry_utils import...")
from src.utils.registry_utils import update_registry_entry
print("   ✅ registry_utils imported")

print("2. Testing image_utils import...")
from src.utils.image_utils import clean_temp_folder
print("   ✅ image_utils imported")

print("3. Testing orchestrator_tools import...")
from src.visual_comic_crew.tools.orchestrator_tools import StatusTrackerTool
print("   ✅ orchestrator_tools imported")

print("\n✨ All imports successful!")
