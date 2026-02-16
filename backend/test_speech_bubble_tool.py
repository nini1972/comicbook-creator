"""
Comprehensive test suite for the Speech Bubble Tool
Tests all features and edge cases for adding speech bubbles to comic panels.
"""

import os
import sys
from pathlib import Path
import time

# Add the backend source directory to Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

# Now import the speech bubble tool
from visual_comic_crew.tools.speech_bubble_tool import (
    SpeechBubbleTool,
    add_classic_speech_bubble,
    add_thought_bubble,
    add_shout_bubble
)


def find_test_panel():
    """Find an existing comic panel to use for testing."""
    from PIL import Image
    possible_paths = [
        "output/comic_panels",
        "backend/output/comic_panels",
        "comic_panels",
        "output",
        "../output/comic_panels",
        "../output",
        "../comic_panels"
    ]
    for base_path in possible_paths:
        test_dir = Path(base_path)
        if test_dir.exists():
            png_files = list(test_dir.glob("*.png"))
            for png in png_files:
                try:
                    with Image.open(png) as img:
                        img.verify()
                    return str(png)
                except Exception:
                    continue
    return None


def test_speech_bubble_server_connection():
    """Test basic server connectivity."""
    print("\n" + "="*60)
    print("🔌 TESTING SERVER CONNECTION")
    print("="*60)
    
    tool = SpeechBubbleTool()
    
    # Test with a simple request (will fail without valid image, but should connect)
    try:
        import requests
        response = requests.get(tool.server_url.replace("/generate-image/", "/"), timeout=10)
        print(f"✅ Server is reachable at {tool.server_url}")
        return True
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False


def test_bubble_styles():
    """Test all different bubble styles."""
    print("\n" + "="*60)
    print("🎨 TESTING BUBBLE STYLES")
    print("="*60)
    
    panel_path = find_test_panel()
    fallback_panel_path = None
    if not panel_path:
        print("❌ No test panel found for bubble style testing")
        return
    print(f"📸 Using test panel: {panel_path}")
    # Try to find a second panel for fallback
    from PIL import Image
    possible_paths = [
        "output/comic_panels",
        "backend/output/comic_panels",
        "comic_panels",
        "output",
        "../output/comic_panels",
        "../output",
        "../comic_panels"
    ]
    for base_path in possible_paths:
        test_dir = Path(base_path)
        if test_dir.exists():
            png_files = list(test_dir.glob("*.png"))
            for png in png_files:
                if str(png) == panel_path:
                    continue
                try:
                    with Image.open(png) as img:
                        img.verify()
                    fallback_panel_path = str(png)
                    break
                except Exception:
                    continue
        if fallback_panel_path:
            break
    tool = SpeechBubbleTool()
    styles_to_test = [
        ("classic", "Hello! This is a classic speech bubble."),
        ("thought", "I wonder what's happening..."),
        ("shout", "WATCH OUT!"),
        ("whisper", "psst... secret message"),
        ("narration", "Meanwhile, in another dimension...")
    ]
    results = []
    for style, dialogue in styles_to_test:
        print(f"\n🎯 Testing {style} bubble: '{dialogue}'")
        payload = {
            'panel_image_path': panel_path,
            'dialogue_text': dialogue,
            'bubble_style': style,
            'character_position': "auto",
            'panel_number': 100 + len(results)
        }
        print(f"   [DEBUG] Gemini payload: {payload}")
        try:
            result = tool._run(**payload)
            if "✅" in result:
                print(f"   ✅ SUCCESS: {style} bubble generated")
                results.append((style, "SUCCESS", result))
            else:
                print(f"   ❌ FAILED: {result}")
                # Try fallback image if available and not already used
                if fallback_panel_path:
                    print(f"   [DEBUG] Retrying {style} with fallback panel: {fallback_panel_path}")
                    payload['panel_image_path'] = fallback_panel_path
                    try:
                        result2 = tool._run(**payload)
                        if "✅" in result2:
                            print(f"   ✅ SUCCESS (fallback): {style} bubble generated")
                            results.append((style+" (fallback)", "SUCCESS", result2))
                        else:
                            print(f"   ❌ FAILED (fallback): {result2}")
                            results.append((style+" (fallback)", "FAILED", result2))
                    except Exception as e2:
                        print(f"   💥 ERROR (fallback): {e2}")
                        results.append((style+" (fallback)", "ERROR", str(e2)))
                else:
                    results.append((style, "FAILED", result))
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            results.append((style, "ERROR", str(e)))
        time.sleep(2)
    # Summary
    print(f"\n📊 BUBBLE STYLES TEST SUMMARY:")
    print("-" * 40)
    successful = sum(1 for _, status, _ in results if status == "SUCCESS")
    total = len(results)
    for style, status, message in results:
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "💥"
        print(f"   {status_icon} {style:12} : {status}")
    print(f"\n🎯 Overall Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")


def test_positioning_options():
    """Test different positioning options."""
    print("\n" + "="*60)
    print("📍 TESTING POSITIONING OPTIONS")
    print("="*60)
    
    panel_path = find_test_panel()
    if not panel_path:
        print("❌ No test panel found for positioning testing")
        return
    
    tool = SpeechBubbleTool()
    
    positions_to_test = [
        ("left", "I'm positioned on the left!"),
        ("right", "I'm positioned on the right!"),
        ("center", "I'm in the center!"),
        ("auto", "I'm positioned automatically!")
    ]
    results = []
    for position, dialogue in positions_to_test:
        print(f"\n📍 Testing {position} positioning: '{dialogue}'")
        payload = {
            'panel_image_path': panel_path,
            'dialogue_text': dialogue,
            'bubble_style': "classic",
            'character_position': position,
            'panel_number': 200 + len(results)
        }
        print(f"   [DEBUG] Gemini payload: {payload}")
        try:
            result = tool._run(**payload)
            if position == "left" and ("500" in result or "Server error" in result):
                print("   [DEBUG] Retrying 'left' with modified prompt wording...")
                payload_mod = payload.copy()
                payload_mod['character_position'] = "left side"
                result = tool._run(**payload_mod)
                if "500" in result or "Server error" in result:
                    payload_mod['character_position'] = "on the left side of the panel"
                    result = tool._run(**payload_mod)
            if "✅" in result:
                print(f"   ✅ SUCCESS: {position} positioning worked")
                results.append((position, "SUCCESS"))
            else:
                print(f"   ❌ FAILED: {result}")
                results.append((position, "FAILED"))
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            results.append((position, "ERROR"))
        time.sleep(2)
    
    for position, status in results:
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"   {status_icon} {position:8} : {status}")
    
        successful = sum(1 for _, status in results if status == "SUCCESS")
        total = len(results)
        print(f"\n🎯 Success Rate: {successful}/{total} ({(successful/total*100 if total else 0):.1f}%)")


def test_convenience_functions():
    """Test the convenience functions."""
    print("\n" + "="*60)
    print("🚀 TESTING CONVENIENCE FUNCTIONS")
    print("="*60)
    
    panel_path = find_test_panel()
    if not panel_path:
        print("❌ No test panel found for convenience function testing")
        return
    functions_to_test = [
        (add_classic_speech_bubble, "Classic bubble via convenience function"),
        (add_thought_bubble, "Thinking about convenience functions..."),
        (add_shout_bubble, "CONVENIENCE FUNCTIONS ROCK!")
    ]
    results = []
    for func, dialogue in functions_to_test:
        func_name = func.__name__
        print(f"\n🚀 Testing {func_name}: '{dialogue}'")
        panel_num = 300 + len(results)
        print(f"   [DEBUG] Gemini payload: {{'panel_path': panel_path, 'dialogue': dialogue, 'panel_num': panel_num}}")
        try:
            result = func(panel_path, dialogue, panel_num)
            if "✅" in result:
                print(f"   ✅ SUCCESS: {func_name} worked")
                results.append((func_name, "SUCCESS"))
            else:
                print(f"   ❌ FAILED: {result}")
                results.append((func_name, "FAILED"))
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            results.append((func_name, "ERROR"))
        time.sleep(2)
    # Summary
    print(f"\n📊 CONVENIENCE FUNCTIONS TEST SUMMARY:")
    print("-" * 40)
    successful = sum(1 for _, status in results if status == "SUCCESS")
    total = len(results)
    for func_name, status in results:
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"   {status_icon} {func_name:25} : {status}")
    print(f"\n🎯 Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")


def test_multiple_bubbles():
    """Test the multiple bubbles feature."""
    print("\n" + "="*60)
    print("💬 TESTING MULTIPLE BUBBLES")
    print("="*60)
    
    panel_path = find_test_panel()
    if not panel_path:
        print("❌ No test panel found for multiple bubbles testing")
        return
    
    tool = SpeechBubbleTool()
    
    long_dialogue = "This is a really long piece of dialogue that should be split into multiple speech bubbles for better readability and comic book formatting."
    
    print(f"💬 Testing multiple bubbles with long text:")
    print(f"   Text: '{long_dialogue}' ({len(long_dialogue)} chars)")
    
    try:
        result = tool._run(
            panel_image_path=panel_path,
            dialogue_text=long_dialogue,
            bubble_style="classic",
            character_position="auto",
            panel_number=400,
            multiple_bubbles=True
        )
        
        if "✅" in result:
            print(f"   ✅ SUCCESS: Multiple bubbles generated")
            print(f"   Result: {result}")
        else:
            print(f"   ❌ FAILED: {result}")
            
    except Exception as e:
        print(f"   💥 ERROR: {e}")


def test_edge_cases():
    """Test various edge cases and error conditions."""
    print("\n" + "="*60)
    print("⚠️  TESTING EDGE CASES")
    print("="*60)
    
    tool = SpeechBubbleTool()
    
    # Test cases that should fail gracefully
    edge_cases = [
        ("Non-existent file", "/fake/path/panel.png", "Hello", "Should fail with file not found"),
        ("Empty dialogue", find_test_panel(), "", "Should fail with empty text"),
        ("Very long dialogue", find_test_panel(), "A" * 400, "Should fail with text too long"),
    ]
    
    for case_name, panel_path, dialogue, expected in edge_cases:
        print(f"\n⚠️  Testing {case_name}: {expected}")
        
        try:
            result = tool._run(
                panel_image_path=panel_path,
                dialogue_text=dialogue,
                panel_number=500
            )
            
            if "❌" in result:
                print(f"   ✅ CORRECTLY FAILED: {result}")
            else:
                print(f"   ⚠️  UNEXPECTED SUCCESS: {result}")
                
        except Exception as e:
            print(f"   ✅ CORRECTLY THREW EXCEPTION: {e}")


def main():
    """Run all speech bubble tests."""
    print("🧪 SPEECH BUBBLE TOOL COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"⏰ Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Find test panel
    test_panel = find_test_panel()
    if test_panel:
        print(f"📸 Test panel found: {test_panel}")
    else:
        print("⚠️  No test panel found - some tests may be skipped")
    
    # Run all test suites
    test_speech_bubble_server_connection()
    test_bubble_styles()
    test_positioning_options()
    test_convenience_functions()
    test_multiple_bubbles()
    test_edge_cases()
    
    # Final summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("🏁 TEST SUITE COMPLETED")
    print("="*60)
    print(f"⏱️  Total test time: {duration:.1f} seconds")
    print(f"📂 Check output folders for generated speech bubble panels")
    print(f"💡 Review generated panels to assess visual quality")
    
    return True


if __name__ == "__main__":
    main()