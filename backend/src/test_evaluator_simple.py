#!/usr/bin/env python3
"""
Simple test for Panel Validation Tool - Good and Evil Comic Scenario
"""

from visual_comic_crew.tools.panel_validation_tool import PanelValidationTool

# This simulates the Visual Director's output for the "good and evil" comic
# where only Panel 1 was actually generated, but it referenced 6 panels
fake_generation_results = """
Panel Generation Results:
- Panel 1: server_generated_gemini-image-tutorial_1758549637001.png
- Panel 2: server_generated_gemini-image-tutorial_1758549637002.png
- Panel 3: server_generated_gemini-image-tutorial_1758549637003.png
- Panel 4: server_generated_gemini-image-tutorial_1758549637004.png
- Panel 5: server_generated_gemini-image-tutorial_1758549637005.png
- Panel 6: server_generated_gemini-image-tutorial_1758549637006.png

Summary:
- Total panels attempted: 6
- Successfully generated: 6
- Failed: 0
"""

print("🧪 Testing Panel Validation Tool with 'Good and Evil' Comic")
print("=" * 60)
print("\n📋 Scenario: Only panel 1 exists, but 6 panels were reported")

# Create and run the validation tool
validator = PanelValidationTool()
validation_report = validator._run(fake_generation_results, expected_panel_count=6)

print("\n📊 VALIDATION REPORT:")
print("=" * 40)
print(validation_report)

# Check results
if "FAIL" in validation_report:
    print("\n✅ SUCCESS: Evaluator correctly identified missing panels!")
else:
    print("\n❌ ISSUE: Evaluator should have failed validation!")

print("\n🎯 The evaluator should prevent this comic from reaching assembly!")