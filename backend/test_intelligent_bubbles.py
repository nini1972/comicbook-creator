"""
Demo script to showcase the new intelligent speech bubble color and transparency features.
Tests the enhanced emotion detection and automatic color selection.
"""

import sys
from pathlib import Path

# Add the backend source directory to Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from visual_comic_crew.tools.speech_bubble_tool import (
    SpeechBubbleTool,
    add_emotional_bubble
)


def test_intelligent_color_selection():
    """Test the new intelligent color selection and emotion detection features."""
    
    print("🎨 TESTING INTELLIGENT SPEECH BUBBLE COLORS & TRANSPARENCY")
    print("=" * 70)
    
    # Find a test panel
    possible_paths = ["output/comic_panels", "backend/output/comic_panels", "comic_panels"]
    panel_path = None
    
    for base_path in possible_paths:
        test_dir = Path(base_path)
        if test_dir.exists():
            png_files = list(test_dir.glob("*.png"))
            if png_files:
                panel_path = str(png_files[0])
                break
    
    if not panel_path:
        print("❌ No test panel found. Please ensure you have comic panels in output/comic_panels/")
        return
    
    print(f"📸 Using test panel: {panel_path}")
    print()
    
    tool = SpeechBubbleTool()
    
    # Test cases with different emotions and expected color behaviors
    test_cases = [
        {
            "dialogue": "Wow! This is amazing!",
            "expected_emotion": "excited",
            "description": "Excited dialogue should get yellow/bright colors"
        },
        {
            "dialogue": "I'm so angry about this!",
            "expected_emotion": "angry", 
            "description": "Angry dialogue should get red colors with intense effects"
        },
        {
            "dialogue": "psst... I have a secret to tell you",
            "expected_emotion": "secretive",
            "description": "Whispered secrets should get semi-transparent styling"
        },
        {
            "dialogue": "I love you with all my heart",
            "expected_emotion": "romantic",
            "description": "Romantic dialogue should get pink/warm colors"
        },
        {
            "dialogue": "I'm so confused... what does this mean?",
            "expected_emotion": "confused",
            "description": "Confused dialogue should get light blue colors"
        },
        {
            "dialogue": "I feel so sad and down today",
            "expected_emotion": "sad",
            "description": "Sad dialogue should get blue with transparency"
        },
        {
            "dialogue": "That ghost was terrifying!",
            "expected_emotion": "fearful",
            "description": "Fearful dialogue should get dark colors with shadows"
        },
        {
            "dialogue": "Hello, how are you today?",
            "expected_emotion": "neutral",
            "description": "Neutral dialogue should get standard white/classic colors"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🎭 Test {i}: {test_case['description']}")
        print(f"   Dialogue: \"{test_case['dialogue']}\"")
        
        # Test emotion detection
        emotion_data = tool._analyze_dialogue_emotion(test_case['dialogue'])
        print(f"   🧠 Detected emotion: {emotion_data['emotion']} (expected: {test_case['expected_emotion']})")
        print(f"   🎨 Suggested color: {emotion_data['suggested_color']}")
        print(f"   👻 Transparency: {emotion_data['suggested_transparency']}")
        if emotion_data['suggested_effects']:
            print(f"   ✨ Effects: {', '.join(emotion_data['suggested_effects'])}")
        
        # Test intelligent color selection
        color_data = tool._get_intelligent_color("auto", "classic", test_case['dialogue'], True)
        print(f"   🎯 Final color choice: {color_data['color']}")
        print(f"   📊 Intensity: {color_data['intensity']}")
        
        # Verify emotion detection accuracy
        if emotion_data['emotion'] == test_case['expected_emotion']:
            print(f"   ✅ Emotion detection: CORRECT")
        else:
            print(f"   ⚠️  Emotion detection: Expected {test_case['expected_emotion']}, got {emotion_data['emotion']}")
        
        print()
    
    print("🚀 TESTING LIVE BUBBLE GENERATION WITH AUTO-ENHANCEMENT")
    print("=" * 70)
    
    # Test a few live generations with the new features
    live_tests = [
        "Wow! This comic tool is fantastic!",
        "psst... want to see something cool?", 
        "I'm so angry about this bug!"
    ]
    
    for i, dialogue in enumerate(live_tests, 1):
        print(f"\n🎨 Live Test {i}: Creating bubble with auto-enhancement")
        print(f"   Text: \"{dialogue}\"")
        
        try:
            # Use the new add_emotional_bubble function
            result = add_emotional_bubble(panel_path, dialogue, panel_num=500 + i)
            
            if "✅" in result:
                print(f"   ✅ SUCCESS: {result}")
            else:
                print(f"   ❌ FAILED: {result}")
                
        except Exception as e:
            print(f"   💥 ERROR: {e}")
    
    print("\n🎉 INTELLIGENT BUBBLE TESTING COMPLETED!")
    print("=" * 70)
    print("💡 New Features Tested:")
    print("   ✅ Emotion detection from dialogue text")
    print("   ✅ Intelligent color selection based on context")
    print("   ✅ Automatic transparency adjustment")
    print("   ✅ Dynamic visual effects (glow, shadows, etc.)")
    print("   ✅ Enhanced convenience functions")
    print("   ✅ Auto-enhancement toggle")


if __name__ == "__main__":
    test_intelligent_color_selection()