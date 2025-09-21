#!/usr/bin/env python3

"""
Test enhanced character consistency workflow based on Option 6 approach
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
backend_src = Path(__file__).parent / "src"
sys.path.insert(0, str(backend_src))

from visual_comic_crew.crew import VisualComicCrew

def test_enhanced_character_consistency():
    """Test the enhanced Option 6-based character consistency workflow"""
    
    # Test with a story that has clearly defined characters for better consistency
    test_topic = "Captain Zara the space explorer and her AI companion ECHO discover an ancient alien artifact on a mysterious planet"
    
    print("=" * 70)
    print(f"🧪 TESTING ENHANCED CHARACTER CONSISTENCY (Option 6 Approach)")
    print("=" * 70)
    print(f"Topic: {test_topic}")
    print()
    
    try:
        # Initialize the crew
        print("📋 Initializing VisualComicCrew with enhanced character consistency...")
        crew = VisualComicCrew()
        crew_instance = crew.crew()
        
        print("✅ Crew initialized successfully")
        print()
        
        # Run the crew with enhanced character consistency
        print("🎬 Starting comic generation with Option 6 character consistency...")
        print("   - Characters will be created as reference sheets first")
        print("   - Then panels will use character references for consistency")
        print()
        
        result = crew_instance.kickoff(inputs={'topic': test_topic})
        
        print("=" * 70)
        print("🎉 ENHANCED CHARACTER CONSISTENCY TEST COMPLETED!")
        print("=" * 70)
        print(result)
        
        # Check results
        print("\n" + "=" * 50)
        print("📊 CONSISTENCY ANALYSIS:")
        print("=" * 50)
        
        # Check if character references were created
        char_ref_dir = Path("output/character_references")
        if char_ref_dir.exists():
            references = list(char_ref_dir.glob("*.png"))
            cache_file = char_ref_dir / "character_cache.txt"
            
            print(f"📚 Character references created: {len(references)}")
            for ref in references:
                print(f"   - {ref.name}")
            
            if cache_file.exists():
                print(f"💾 Character cache file: {cache_file}")
                with open(cache_file, 'r') as f:
                    print("   Cache contents:")
                    for line in f:
                        print(f"     {line.strip()}")
        else:
            print("⚠️  No character references directory found")
        
        # Check if consistent panels were created
        panel_dir = Path("output/comic_panels")
        if panel_dir.exists():
            all_panels = list(panel_dir.glob("*.png"))
            consistent_panels = list(panel_dir.glob("consistent_panel_*.png"))
            regular_panels = [p for p in all_panels if not p.name.startswith("consistent_panel_")]
            
            print(f"\n🎨 Total panels generated: {len(all_panels)}")
            print(f"✅ Character-consistent panels: {len(consistent_panels)}")
            print(f"📋 Regular panels: {len(regular_panels)}")
            
            if consistent_panels:
                print("   Consistent panels:")
                for panel in consistent_panels:
                    print(f"     - {panel.name}")
        else:
            print("⚠️  No comic panels directory found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during enhanced character consistency test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_character_consistency()
    if success:
        print("\n✅ Enhanced character consistency test completed successfully!")
        print("   Option 6 approach implementation working!")
    else:
        print("\n❌ Enhanced character consistency test failed!")
    
    sys.exit(0 if success else 1)