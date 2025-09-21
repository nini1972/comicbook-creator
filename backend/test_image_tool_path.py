#!/usr/bin/env python3
"""
Test the GeminiImageTool to verify path fix
"""
import sys
import os
sys.path.append('.')

from src.visual_comic_crew.tools.gemini_image_tool import GeminiImageTool

def test_image_tool():
    """Test the image tool directly"""
    print("Testing GeminiImageTool with path fix...")
    
    tool = GeminiImageTool()
    
    # Test with a simple prompt
    result = tool._run("a simple blue bird on a branch")
    
    print(f"Tool result: {result}")
    
    # Check if result contains correct path
    if "output/comic_panels/" in result:
        print("✓ Path fix is working! Tool returns correct path.")
        
        # Extract filename from result
        import re
        match = re.search(r'output/comic_panels/([^"]*)', result)
        if match:
            filename = match.group(1)
            file_path = os.path.join("output", "comic_panels", filename)
            
            if os.path.exists(file_path):
                print(f"✓ Image file exists: {file_path}")
                return True
            else:
                print(f"✗ Image file not found: {file_path}")
        else:
            print("✗ Could not extract filename from result")
    else:
        print("✗ Path fix not working - result doesn't contain output/comic_panels/")
        
    return False

if __name__ == "__main__":
    test_image_tool()
