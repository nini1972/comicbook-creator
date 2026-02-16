"""
Quick test of Speech Bubble Tool with a specific valid panel
"""

import os
import sys
from pathlib import Path

# Add the backend source directory to Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from visual_comic_crew.tools.speech_bubble_tool import SpeechBubbleTool

def main():
    """Test speech bubbles with a specific valid panel."""
    print("🧪 SPEECH BUBBLE TOOL - QUICK TEST")
    print("="*50)
    
    # Use a specific panel that should exist
    panel_path = "output/comic_panels/consistent_panel_001_echo_1760020377554.png"
    
    # Check if the panel exists
    if not Path(panel_path).exists():
        print(f"❌ Panel not found: {panel_path}")
        return
    
    print(f"📸 Using panel: {panel_path}")
    
    # Create tool and test basic functionality
    tool = SpeechBubbleTool()
    
    print("\n🎯 Testing classic speech bubble...")
    result = tool._run(
        panel_image_path=panel_path,
        dialogue_text="Hello there! This is a test speech bubble.",
        bubble_style="classic",
        character_position="auto",
        panel_number=999
    )
    
    print(f"Result: {result}")
    
    if "✅" in result:
        print("✅ Speech bubble test successful!")
        print("📂 Check the output folder for the generated panel with speech bubble")
    else:
        print("❌ Speech bubble test failed")
        print("🔍 Check the Gemini server logs for details")

if __name__ == "__main__":
    main()