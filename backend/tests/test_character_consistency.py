#!/usr/bin/env python3

"""
Test character consistency workflow
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from visual_comic_crew.crew import VisualComicCrew

def test_character_consistency():
    """Test the character consistency workflow with a simple story"""
    
    # Test with a story that has named characters
    test_topic = "Lyra the brave astronaut discovers a hidden space station with her robot companion Nimbus"
    
    print("=" * 60)
    print(f"🧪 TESTING CHARACTER CONSISTENCY WORKFLOW")
    print("=" * 60)
    print(f"Topic: {test_topic}")
    print()
    
    try:
        # Initialize the crew
        print("📋 Initializing VisualComicCrew...")
        crew = VisualComicCrew()
        crew_instance = crew.crew()
        
        print("✅ Crew initialized successfully")
        print()
        
        # Run the crew with character consistency
        print("🎬 Starting comic generation with character consistency...")
        result = crew_instance.kickoff(inputs={'topic': test_topic})
        
        print("=" * 60)
        print("🎉 CHARACTER CONSISTENCY TEST COMPLETED!")
        print("=" * 60)
        print(result)
        
        # Check if character references were created
        char_ref_dir = Path("output/character_references")
        if char_ref_dir.exists():
            references = list(char_ref_dir.glob("*.png"))
            print(f"\n📚 Character references created: {len(references)}")
            for ref in references:
                print(f"   - {ref.name}")
        
        # Check if consistent panels were created
        panel_dir = Path("output/comic_panels")
        if panel_dir.exists():
            consistent_panels = list(panel_dir.glob("consistent_panel_*.png"))
            print(f"\n🎨 Consistent character panels: {len(consistent_panels)}")
            for panel in consistent_panels:
                print(f"   - {panel.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during character consistency test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_character_consistency()
    if success:
        print("\n✅ Character consistency test completed successfully!")
    else:
        print("\n❌ Character consistency test failed!")
    
    sys.exit(0 if success else 1)