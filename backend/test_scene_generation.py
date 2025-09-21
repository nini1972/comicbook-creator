#!/usr/bin/env python3
"""
Test the Character Consistency Tool scene generation functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from visual_comic_crew.tools.character_consistency_tool import CharacterConsistencyTool

def test_scene_generation():
    """Test scene generation with character consistency"""
    print("🎬 Testing Character Consistency Tool scene generation...")
    
    tool = CharacterConsistencyTool()
    
    # Test 1: Generate scene with existing character
    print("\n1️⃣ Testing generate_scene with existing character:")
    result = tool._run(
        action="generate_scene",
        character_name="Zara",
        scene_description="Zara exploring a mysterious cave with glowing crystals",
        panel_number=1
    )
    print(f"Result: {result}")
    
    # Test 2: Generate scene with non-existent character
    print("\n2️⃣ Testing generate_scene with non-existent character:")
    result2 = tool._run(
        action="generate_scene",
        character_name="Unknown",
        scene_description="Unknown character in a forest",
        panel_number=2
    )
    print(f"Result: {result2}")

if __name__ == "__main__":
    print("🚀 Character Consistency Tool Scene Generation Test")
    print("=" * 60)
    
    test_scene_generation()
    
    print("\n" + "=" * 60)
    print("🎯 Scene generation test completed!")