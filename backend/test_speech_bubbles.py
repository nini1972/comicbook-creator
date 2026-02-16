"""
Test script for the new speech bubble functionality in Image Refinement Tool.
This script tests adding speech bubbles to existing comic panels.
"""

import sys
from pathlib import Path

# Add the backend src to path for imports
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

from src.visual_comic_crew.tools.image_refinement_tool import ImageRefinementTool


def test_speech_bubble_functionality():
    """Test the new speech bubble features with various styles and text."""
    print("🧪 Testing Speech Bubble Functionality")
    print("=" * 60)
    
    # Initialize the tool
    tool = ImageRefinementTool()
    
    # Find an existing panel to test with
    panels_dir = Path("output/comic_panels")
    if not panels_dir.exists():
        print("❌ No comic panels directory found. Generate a comic first.")
        return
    
    # Look for recent panel files
    panel_files = list(panels_dir.glob("*.png"))
    if not panel_files:
        print("❌ No panel files found. Generate a comic first.")
        return
    
    # Use the most recent panel for testing
    test_panel = max(panel_files, key=lambda p: p.stat().st_mtime)
    print(f"📷 Using test panel: {test_panel.name}")
    print(f"   File size: {test_panel.stat().st_size:,} bytes")
    
    # Test cases for different speech bubble styles
    test_cases = [
        {
            "name": "Classic Speech Bubble",
            "dialogue": "Hello there! How are you doing today?",
            "style": "classic",
            "position": "auto"
        },
        {
            "name": "Thought Bubble", 
            "dialogue": "I wonder what will happen next...",
            "style": "thought",
            "position": "center"
        },
        {
            "name": "Shout Bubble",
            "dialogue": "WATCH OUT!",
            "style": "shout", 
            "position": "left"
        },
        {
            "name": "Whisper Bubble",
            "dialogue": "Psst... over here",
            "style": "whisper",
            "position": "right"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   Text: '{test_case['dialogue']}'")
        print(f"   Style: {test_case['style']}")
        print(f"   Position: {test_case['position']}")
        
        try:
            result = tool._run(
                base_image_path=str(test_panel),
                refinement_prompt="",  # No additional refinements, just speech bubble
                panel_number=i,
                add_speech_bubble=True,
                dialogue_text=test_case['dialogue'],
                bubble_style=test_case['style'],
                character_position=test_case['position']
            )
            
            print(f"   Result: {result}")
            
            # Check if result indicates success
            if result.startswith("✅"):
                results.append(f"✅ {test_case['name']}: SUCCESS")
            else:
                results.append(f"❌ {test_case['name']}: FAILED - {result}")
                
        except Exception as e:
            error_result = f"❌ {test_case['name']}: ERROR - {str(e)}"
            print(f"   Error: {e}")
            results.append(error_result)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SPEECH BUBBLE TEST RESULTS")
    print("=" * 60)
    
    for result in results:
        print(result)
    
    success_count = sum(1 for r in results if r.startswith("✅"))
    total_count = len(results)
    
    print(f"\n📈 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 All speech bubble tests passed!")
    elif success_count > 0:
        print("⚠️ Some tests passed - speech bubble functionality is working but may need refinement")
    else:
        print("❌ All tests failed - check Gemini server and image processing")
    
    # Check output directory for new files
    print(f"\n📁 Check output/comic_panels/ for new files with 'speech_bubble_panel_' prefix")


def test_combined_refinement_and_speech():
    """Test combining regular refinement with speech bubble addition."""
    print("\n🔄 Testing Combined Refinement + Speech Bubble")
    print("=" * 60)
    
    tool = ImageRefinementTool()
    
    # Find an existing panel
    panels_dir = Path("output/comic_panels")
    panel_files = list(panels_dir.glob("*.png"))
    
    if not panel_files:
        print("❌ No panel files found for combined test.")
        return
    
    test_panel = panel_files[0]
    print(f"📷 Using panel: {test_panel.name}")
    
    try:
        result = tool._run(
            base_image_path=str(test_panel),
            refinement_prompt="Make the colors more vibrant and add dramatic lighting",
            panel_number=99,
            add_speech_bubble=True,
            dialogue_text="This looks amazing with the new lighting!",
            bubble_style="classic",
            character_position="auto"
        )
        
        print(f"Combined test result: {result}")
        
    except Exception as e:
        print(f"Combined test error: {e}")


def main():
    """Run all speech bubble tests."""
    print("🚀 Starting Speech Bubble Testing Suite")
    print("Make sure the Gemini Image Server is running on http://127.0.0.1:8000")
    
    # Check if server is accessible
    import requests
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        print("✅ Gemini Image Server appears to be running")
    except:
        print("⚠️ Cannot reach Gemini Image Server - tests may fail")
        print("   Make sure to start the server with: python gemini_image_server.py")
    
    # Run tests
    test_speech_bubble_functionality()
    test_combined_refinement_and_speech()
    
    print("\n✨ Speech bubble testing complete!")
    print("Check the generated files and visually inspect the speech bubbles.")


if __name__ == "__main__":
    main()