#!/usr/bin/env python3
"""
Test connectivity to Gemini Image Tutorial server and GeminiImageTool
"""
import sys
import os
import requests
import time

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append('.')

def test_gemini_server():
    """Test if Gemini Image Tutorial server is running"""
    print("Testing Gemini Image Tutorial server connectivity...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Gemini server is running and healthy")
            return True
        else:
            print(f"⚠ Gemini server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Gemini server on port 8000")
        print("  Make sure the Gemini Image Tutorial server is running")
        return False
    except requests.exceptions.Timeout:
        print("✗ Timeout connecting to Gemini server")
        return False
    except Exception as e:
        print(f"✗ Error connecting to Gemini server: {e}")
        return False

def test_image_generation():
    """Test direct image generation via API"""
    print("\nTesting direct image generation...")
    
    try:
        payload = {"prompt": "a simple blue bird"}
        response = requests.post(
            "http://localhost:8000/generate-comic-image",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Image generation successful: {result}")
            return True, result
        else:
            print(f"✗ Image generation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"✗ Error during image generation: {e}")
        return False, None

def test_gemini_image_tool():
    """Test the GeminiImageTool"""
    print("\nTesting GeminiImageTool...")
    
    try:
        from src.visual_comic_crew.tools.gemini_image_tool import GeminiImageTool
        
        tool = GeminiImageTool()
        result = tool._run("a simple blue bird")
        
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
        
    except Exception as e:
        print(f"✗ Error testing GeminiImageTool: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("GEMINI IMAGE TUTORIAL CONNECTIVITY TEST")
    print("="*60)
    
    # Test server connectivity
    server_ok = test_gemini_server()
    
    if server_ok:
        # Test direct API
        api_ok, api_result = test_image_generation()
        
        if api_ok:
            # Test the tool
            tool_ok = test_gemini_image_tool()
            
            if tool_ok:
                print("\n🎉 ALL TESTS PASSED!")
                print("The Gemini Image Tutorial integration is working correctly.")
            else:
                print("\n⚠ Tool test failed - check GeminiImageTool implementation")
        else:
            print("\n⚠ Direct API test failed - check Gemini server configuration")
    else:
        print("\n❌ Server connectivity failed")
        print("Please ensure:")
        print("1. Gemini Image Tutorial server is running")
        print("2. Server is listening on port 8000")
        print("3. No firewall blocking the connection")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
