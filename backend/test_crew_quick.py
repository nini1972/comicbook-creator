#!/usr/bin/env python3
"""
Quick test of character consistency within crew workflow.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from visual_comic_crew.crew import VisualComicCrew

def test_crew_character_consistency():
    """Test crew with character consistency focus"""
    print("🚀 Testing crew with enhanced character consistency...")
    
    # Simple story with clear character
    story = "A brave astronaut named Alex explores a mysterious cave on an alien planet and discovers a glowing crystal."
    
    crew = VisualComicCrew()
    
    try:
        result = crew.crew().kickoff(inputs={
            'topic': story,
            'user_preferences': 'Focus on character consistency for Alex the astronaut'
        })
        
        print("\n" + "=" * 60)
        print("✅ Crew test completed!")
        print("Result type:", type(result))
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"❌ Crew test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_crew_character_consistency()