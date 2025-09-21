#!/usr/bin/env python3
"""
Test the updated Character Consistency Tool with proper schema-based parameters.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from visual_comic_crew.tools.character_consistency_tool import CharacterConsistencyTool

def test_schema_based_tool():
    """Test the Character Consistency Tool with schema-based parameters"""
    print("🔧 Testing Character Consistency Tool with schema-based parameters...")
    
    tool = CharacterConsistencyTool()
    
    # Test 1: Create character with schema-based parameters
    print("\n1️⃣ Testing create_character with schema parameters:")
    result = tool._run(
        action="create_character",
        character_name="Zara",
        character_description="Space explorer in futuristic suit with short dark hair and confident expression"
    )
    print(f"Result: {result}")
    
    # Test 2: List characters
    print("\n2️⃣ Testing list_characters:")
    result2 = tool._run(action="list_characters")
    print(f"Result: {result2}")
    
    # Test 3: Test with missing parameters
    print("\n3️⃣ Testing with missing parameters:")
    result3 = tool._run(action="create_character", character_name="TestChar")
    print(f"Result: {result3}")

if __name__ == "__main__":
    print("🚀 Schema-based Character Consistency Tool Test")
    print("=" * 50)
    
    test_schema_based_tool()
    
    print("\n" + "=" * 50)
    print("🎯 Schema test completed!")