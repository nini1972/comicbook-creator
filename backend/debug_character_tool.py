#!/usr/bin/env python3
"""
Debug script to test Character Consistency Tool directly
and understand why it's failing in the crew workflow.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from visual_comic_crew.tools.character_consistency_tool import CharacterConsistencyTool

def test_tool_directly():
    """Test the Character Consistency Tool with direct method calls"""
    print("🔧 Testing Character Consistency Tool directly...")
    
    tool = CharacterConsistencyTool()
    
    # Test 1: Create character reference
    print("\n1️⃣ Testing create_character_reference method:")
    result = tool.create_character_reference(
        character_name="Zara",
        character_description="Space explorer in futuristic suit with short dark hair and confident expression",
        existing_image_path=None
    )
    print(f"Result: {result}")
    
    # Test 2: Test _run method with proper parameters
    print("\n2️⃣ Testing _run method with create_character action:")
    result2 = tool._run(
        action="create_character",
        character_name="TestCharacter", 
        character_description="Test character for debugging",
        existing_image_path=None
    )
    print(f"Result: {result2}")
    
    # Test 3: List characters
    print("\n3️⃣ Testing list_characters:")
    result3 = tool._run(action="list_characters")
    print(f"Result: {result3}")
    
    # Test 4: Test invalid action
    print("\n4️⃣ Testing invalid action:")
    result4 = tool._run(action="invalid_action")
    print(f"Result: {result4}")

def test_tool_as_crew_would():
    """Test how CrewAI would call the tool"""
    print("\n🤖 Testing how CrewAI calls the tool...")
    
    tool = CharacterConsistencyTool()
    
    # This is likely how CrewAI calls it based on the task description
    print("\n5️⃣ Testing basic tool call (no action parameter):")
    try:
        # Try to call tool with simple string like CrewAI might
        result = tool._run("create_character")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Try with just action parameter
    print("\n6️⃣ Testing with just action:")
    result = tool._run(action="create_character")
    print(f"Result: {result}")

if __name__ == "__main__":
    print("🚀 Character Consistency Tool Debug Session")
    print("=" * 50)
    
    test_tool_directly()
    test_tool_as_crew_would()
    
    print("\n" + "=" * 50)
    print("🎯 Debug session completed!")