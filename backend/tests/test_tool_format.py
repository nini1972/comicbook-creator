#!/usr/bin/env python3
"""
Test script to verify the Gemini Image Generator tool works with proper arguments.
"""

import sys
import os

# Add the project path to sys.path
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_path, 'src'))

from visual_comic_crew.tools.gemini_image_tool import GeminiImageTool

def test_correct_format():
    """Test with correct string format (should work)."""
    print("🧪 Testing Gemini Image Generator with CORRECT format")
    print("=" * 60)
    
    tool = GeminiImageTool()
    
    # Correct format - simple string
    test_prompt = "A cute cartoon mouse looking at the moon, whimsical children's book style"
    
    try:
        print(f"✅ Testing with prompt: '{test_prompt[:50]}...'")
        result = tool._run(prompt=test_prompt)
        print(f"✅ SUCCESS: {result}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_incorrect_format():
    """Test with incorrect dictionary format (should fail)."""
    print("\n🧪 Testing Gemini Image Generator with INCORRECT format")
    print("=" * 60)
    
    tool = GeminiImageTool()
    
    # Incorrect format - dictionary (this is what was causing the error)
    test_prompt_dict = {
        "description": "A cute cartoon mouse looking at the moon",
        "type": "str"
    }
    
    try:
        print(f"❌ Testing with dict prompt: {test_prompt_dict}")
        result = tool._run(prompt=test_prompt_dict)
        
        # Check if the result contains an error message
        if "Error:" in result and "must be a string" in result:
            print(f"✅ EXPECTED VALIDATION ERROR: {result}")
            return True
        else:
            print(f"⚠️  UNEXPECTED SUCCESS: {result}")
            return False
    except Exception as e:
        print(f"✅ EXPECTED FAILURE: {e}")
        return True

if __name__ == "__main__":
    print("🚀 Testing Gemini Image Generator Tool Argument Formats")
    print("=" * 70)
    
    try:
        # Test correct format
        correct_works = test_correct_format()
        
        # Test incorrect format
        incorrect_fails = test_incorrect_format()
        
        print("\n📊 SUMMARY:")
        print("=" * 30)
        print(f"✅ Correct format works: {correct_works}")
        print(f"✅ Incorrect format fails: {incorrect_fails}")
        
        if correct_works and incorrect_fails:
            print("\n🎉 Tool validation is working correctly!")
            print("Visual Director should now use the proper string format.")
        else:
            print("\n⚠️  Tool validation needs investigation.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()