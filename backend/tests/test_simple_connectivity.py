#!/usr/bin/env python3
"""
Simple test to verify Gemini Image Tool connectivity and Python environment
"""
import sys
import os
import requests
import platform

print("=" * 60)
print("PYTHON ENVIRONMENT & GEMINI CONNECTIVITY TEST")
print("=" * 60)

# Check Python version
print(f"Python version: {platform.python_version()}")
print(f"Python executable: {sys.executable}")
print(f"Platform: {platform.platform()}")

# Test basic server connectivity
print("\n--- Testing Gemini Server Connectivity ---")
try:
    response = requests.post(
        "http://localhost:8000/generate-image/",
        json={"prompt": "a simple red apple"},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Server responded successfully!")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Message: {result.get('message', 'no message')}")
        print(f"Image path: {result.get('image_path', 'no path')}")
    else:
        print(f"✗ Server error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"✗ Connection failed: {e}")

# Test GeminiImageTool import and usage
print("\n--- Testing GeminiImageTool ---")
try:
    # Add path
    sys.path.append('src')
    from visual_comic_crew.tools.gemini_image_tool import GeminiImageTool
    
    print("✓ GeminiImageTool imported successfully")
    
    # Test the tool
    tool = GeminiImageTool()
    result = tool._run("a simple blue bird")
    
    if "Error:" in result:
        print(f"✗ Tool error: {result}")
    else:
        print(f"✓ Tool success: {result}")
        
except Exception as e:
    print(f"✗ Tool test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)