#!/usr/bin/env python3
"""
Test the PanelValidationTool fix for handling different filename formats.
"""
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.visual_comic_crew.tools.panel_validation_tool import PanelValidationTool

def test_filename_normalization():
    """Test the filename normalization logic."""
    tool = PanelValidationTool()

    # Test cases
    test_cases = [
        # Full path (CharacterConsistencyTool format)
        "output/comic_panels/consistent_panel_002_mittens_1758729792769.png",
        # Descriptive text (GeminiImageTool format)
        "Image generated successfully. Filename: server_generated_gemini-image-tutorial_1758729779661.png",
        # Direct filename
        "direct_filename.png",
        # Path with backslashes
        "output\\comic_panels\\another_file.png"
    ]

    print("Testing filename normalization:")
    for test_input in test_cases:
        normalized = tool._normalize_filename(test_input)
        print(f"Input: '{test_input}'")
        print(f"Normalized: '{normalized}'")
        print("---")

def test_panel_map_validation():
    """Test validation with mixed input formats."""
    tool = PanelValidationTool()

    # Simulate the panel_map that was causing issues
    panel_map = {
        '1': 'server_generated_gemini-image-tutorial_1758729779661.png',  # Direct filename
        '2': 'output\\comic_panels\\consistent_panel_002_mittens_1758729792769.png',  # Full path
        '3': 'Image generated successfully. Filename: server_generated_gemini-image-tutorial_1758729843941.png',  # Descriptive text
        '4': 'server_generated_gemini-image-tutorial_1758729888751.png',  # Direct filename
        '5': 'server_generated_gemini-image-tutorial_1758729902925.png',  # Direct filename
        '6': 'server_generated_gemini-image-tutorial_1758729918682.png'   # Direct filename
    }

    print("Testing panel validation with mixed formats:")
    print(f"Input panel_map: {panel_map}")

    # Test the validation (this will check file existence)
    result = tool._run(panel_map, expected_panel_count=6)
    print(f"Validation result:\n{result}")

if __name__ == "__main__":
    test_filename_normalization()
    print("\n" + "="*50 + "\n")
    test_panel_map_validation()