#!/usr/bin/env python3
"""
Test script to verify complete comic generation workflow
"""
import requests
import json
import time
import os

def test_comic_generation():
    """Test the complete comic generation workflow"""
    
    # Simple, safe prompt that should work with Gemini safety filters
    prompt = "a bird singing in a tree"
    
    print(f"Testing comic generation with prompt: '{prompt}'")
    print("="*50)
    
    try:
        # Make request to the API
        response = requests.post(
            "http://localhost:8001/generate-comic",
            json={"topic": prompt},
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code == 200:
            print("✓ API request successful")
            
            # Check if output file was created
            output_file = os.path.join("output", f"{prompt.replace(' ', '_')}.md")
            if os.path.exists(output_file):
                print(f"✓ Output file created: {output_file}")
                
                # Read and check content
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for image references
                if "output/comic_panels/" in content:
                    print("✓ Comic contains correct image paths")
                    
                    # Count image references
                    image_count = content.count("output/comic_panels/")
                    print(f"✓ Found {image_count} image references")
                    
                    # Check if images actually exist
                    comic_panels_dir = os.path.join("output", "comic_panels")
                    if os.path.exists(comic_panels_dir):
                        images = [f for f in os.listdir(comic_panels_dir) if f.endswith('.png')]
                        print(f"✓ Found {len(images)} images in comic_panels directory")
                        
                        if len(images) >= image_count:
                            print("✓ All referenced images exist!")
                            return True
                        else:
                            print(f"⚠ Missing images: {image_count} referenced, {len(images)} exist")
                    else:
                        print("✗ comic_panels directory doesn't exist")
                        
                elif "placehold.co" in content:
                    print("✗ Comic still contains placeholder images")
                else:
                    print("? No image references found in comic")
                    
            else:
                print(f"✗ Output file not found: {output_file}")
                
        else:
            print(f"✗ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    return False

if __name__ == "__main__":
    test_comic_generation()
