#!/usr/bin/env python3
"""
Test the Gemini server directly with simple prompts.
"""

import requests

def test_simple_prompts():
    """Test simple prompts that should work"""
    url = "http://127.0.0.1:8000/generate-image/"
    
    test_prompts = [
        "astronaut in space suit",
        "person standing",
        "character in futuristic suit",
        "space explorer"
    ]
    
    for prompt in test_prompts:
        print(f"\n🧪 Testing prompt: '{prompt}'")
        try:
            response = requests.post(url, json={"prompt": prompt}, timeout=30)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_simple_prompts()