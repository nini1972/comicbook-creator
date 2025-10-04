#!/usr/bin/env python3
"""
Test script for the new centralized story metadata system
"""

import sys
import os
from pathlib import Path

# Add the backend source directory to the Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from visual_comic_crew.crew import VisualComicCrew

def test_centralized_metadata():
    """Test the comic generation with the new centralized metadata approach."""
    try:
        print("=== Testing Centralized Story Metadata System ===")
        print()
        
        # Initialize the crew
        crew = VisualComicCrew()
        
        # Define a simple test topic
        test_topic = "a cat learning to fly with makeshift wings"
        
        print(f"Topic: {test_topic}")
        print()
        print("Starting comic generation with centralized metadata...")
        print()
        
        # Run the crew with the test topic
        result = crew.crew().kickoff(inputs={'topic': test_topic})
        
        print()
        print("=== Comic Generation Complete ===")
        print()
        print("Result:")
        print(result)
        
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing the new centralized story metadata system...")
    success = test_centralized_metadata()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)