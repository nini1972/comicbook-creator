"""
Simple test to check if orchestrator tools can be imported
"""
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🧪 Testing Orchestrator Tools Import...")

try:
    print("1. Importing StatusTrackerTool...")
    from src.visual_comic_crew.tools.orchestrator_tools import StatusTrackerTool
    print("   ✅ StatusTrackerTool imported successfully")
    
    print("2. Creating StatusTrackerTool instance...")
    tracker = StatusTrackerTool()
    print("   ✅ StatusTrackerTool instance created")
    
    print("\n✨ Import test successful!")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
