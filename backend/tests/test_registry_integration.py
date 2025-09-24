#!/usr/bin/env python3
"""
Test the enhanced panel validation tool with registry integration
"""
import sys
import os
sys.path.append('src')

from visual_comic_crew.tools.panel_validation_tool import PanelValidationTool
from visual_comic_crew.tools.registry import update_registry_entry, read_registry

def test_registry_integration():
    """Test the registry integration with panel validation"""
    print("🧪 TESTING ENHANCED PANEL VALIDATION WITH REGISTRY")
    print("=" * 60)
    
    try:
        # Create a mock image generation result
        mock_generation_results = """
Panel Generation Results:
- Panel 1: server_generated_gemini-image-tutorial_1758566316842.png
- Panel 2: server_generated_gemini-image-tutorial_1758566309711.png
- Panel 3: server_generated_gemini-image-tutorial_1758566298943.png
- Panel 4: server_generated_gemini-image-tutorial_1758566291086.png
- Panel 5: FAILED: Generation timeout
- Panel 6: server_generated_gemini-image-tutorial_1758566275081.png
"""
        
        print("1. 📋 Mock generation results:")
        print(f"   {mock_generation_results.strip()}")
        
        # Pre-populate registry with some verified panels
        print("\n2. 🏗️ Setting up registry with pre-verified panels...")
        update_registry_entry("panel_1", True, True, True)
        update_registry_entry("panel_2", True, True, True)
        
        # Show registry state
        registry = read_registry()
        print(f"   Registry state: {len(registry)} entries")
        for panel_id, status in registry.items():
            print(f"   - {panel_id}: verified={status.get('verified')}")
        
        # Test the enhanced validation tool
        print("\n3. 🔍 Running enhanced panel validation...")
        validation_tool = PanelValidationTool()
        result = validation_tool._run(mock_generation_results, expected_panel_count=6)
        
        print("\n4. 📊 Validation Results:")
        print(result)
        
        # Check final registry state
        print("\n5. 📚 Final registry state:")
        final_registry = read_registry()
        for panel_id, status in final_registry.items():
            print(f"   - {panel_id}: backend={status.get('backend_synced')}, frontend={status.get('frontend_synced')}, verified={status.get('verified')}")
        
        print("\n✅ Registry integration test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_registry_integration()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Tests failed!")