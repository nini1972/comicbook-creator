#!/usr/bin/env python3
"""
Test script for the Panel Validation Tool to verify it correctly identifies missing panels.
This simulates the "good and evil" comic scenario where only 1 out of 6 panels was generated.
"""

import sys
import os

# Add the project path to sys.path so we can import our modules
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_path, 'src'))

from visual_comic_crew.tools.panel_validation_tool import PanelValidationTool

def test_good_and_evil_scenario():
    """Test with the actual 'good and evil' comic generation results."""
    
    # This simulates the Visual Director's output for the "good and evil" comic
    # where only Panel 1 was actually generated, but it referenced 6 panels
    fake_generation_results = """
Character References:
- Kael: SUCCESS: output\\character_references\\kael_reference.png
- Seraphina: SUCCESS: output\\character_references\\seraphina_reference.png

Panel Generation Results:
- Panel 1: output\\server_generated_gemini-image-tutorial_1758549637001.png
- Panel 2: output\\server_generated_gemini-image-tutorial_1758549637002.png
- Panel 3: output\\server_generated_gemini-image-tutorial_1758549637003.png
- Panel 4: output\\server_generated_gemini-image-tutorial_1758549637004.png
- Panel 5: output\\server_generated_gemini-image-tutorial_1758549637005.png
- Panel 6: output\\server_generated_gemini-image-tutorial_1758549637006.png

Summary:
- Total panels attempted: 6
- Successfully generated: 6
- Failed: 0
"""

    print("🧪 Testing Panel Validation Tool with 'Good and Evil' Comic Scenario")
    print("=" * 70)
    print("\n📋 Scenario: Visual Director reported 6 successful panels, but only panel 1 actually exists")
    print(f"    Existing file: server_generated_gemini-image-tutorial_1758549637001.png")
    print(f"    Missing files: 002, 003, 004, 005, 006")
    
    # Create and run the validation tool
    validator = PanelValidationTool()
    
    print("\n🔍 Running validation...")
    validation_report = validator._run(fake_generation_results, expected_panel_count=6)
    
    print("\n📊 VALIDATION REPORT:")
    print("=" * 50)
    print(validation_report)
    
    # Check if validation correctly identified the problems
    if "FAIL" in validation_report:
        print("\n✅ SUCCESS: Evaluator correctly identified missing panels!")
        if "5" in validation_report and "missing" in validation_report.lower():
            print("✅ SUCCESS: Evaluator correctly counted missing panels!")
        else:
            print("⚠️  WARNING: Evaluator didn't correctly count all missing panels")
    else:
        print("\n❌ FAILURE: Evaluator should have failed validation but didn't!")
    
    return validation_report

def test_perfect_scenario():
    """Test with a scenario where all panels exist (should PASS)."""
    
    # This simulates a successful generation where all files exist
    # Using files we know exist from previous successful runs
    good_generation_results = """
Panel Generation Results:
- Panel 1: server_generated_comicbook_1757954831971.png
- Panel 2: server_generated_comicbook_1757954838951.png
- Panel 3: server_generated_comicbook_1757954852017.png
- Panel 4: server_generated_comicbook_1757954858935.png
- Panel 5: server_generated_comicbook_1757954871364.png
- Panel 6: server_generated_comicbook_1757954877445.png

Summary:
- Total panels attempted: 6
- Successfully generated: 6
- Failed: 0
"""

    print("\n\n🧪 Testing Panel Validation Tool with Perfect Scenario")
    print("=" * 70)
    print("\n📋 Scenario: All 6 panels should exist (from previous successful runs)")
    
    # Create and run the validation tool
    validator = PanelValidationTool()
    
    print("\n🔍 Running validation...")
    validation_report = validator._run(good_generation_results, expected_panel_count=6)
    
    print("\n📊 VALIDATION REPORT:")
    print("=" * 50)
    print(validation_report)
    
    # Check if validation correctly passed
    if "PASS" in validation_report:
        print("\n✅ SUCCESS: Evaluator correctly validated existing panels!")
    else:
        print("\n⚠️  INFO: Some panels may not exist (expected for test environment)")
    
    return validation_report

if __name__ == "__main__":
    print("🚀 Starting Panel Validation Tool Tests")
    print("=" * 70)
    
    try:
        # Test 1: The problematic "good and evil" scenario
        test_good_and_evil_scenario()
        
        # Test 2: A perfect scenario (if files exist)
        test_perfect_scenario()
        
        print("\n🎉 Testing Complete!")
        print("\nThe evaluator should:")
        print("  ✅ Detect missing panels in the 'good and evil' scenario")
        print("  ✅ Provide detailed file existence reports")
        print("  ✅ Return FAIL status for incomplete comics")
        print("  ✅ Prevent broken comics from reaching assembly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()