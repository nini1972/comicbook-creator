"""
Test the Orchestrator and Evaluator Tools
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.visual_comic_crew.tools.orchestrator_tools import (
    WorkflowControlTool, 
    RetryManagerTool, 
    StatusTrackerTool,
    CleanupTool
)
from src.visual_comic_crew.tools.panel_validation_tool import PanelValidationTool
from src.utils.registry_utils import update_registry_entry, read_registry, clear_registry

def test_status_tracker():
    """Test the StatusTrackerTool"""
    print("🧪 Test 1: StatusTrackerTool...")
    
    # Clear registry first
    clear_registry()
    
    # Create some test registry entries
    update_registry_entry("panel_1", "panel_001_test.png", True, True, True)
    update_registry_entry("panel_2", "panel_002_test.png", True, True, True)
    update_registry_entry("panel_3", "panel_003_test.png", True, False, False)  # Not synced
    
    # Test status tracker
    tracker = StatusTrackerTool()
    result = tracker._run(expected_panels=6)
    
    print(f"Status Report:\n{result}")
    
    # Verify results
    assert "panel_1" in result, "Panel 1 should be in status report"
    assert "panel_2" in result, "Panel 2 should be in status report"
    assert "3 of 6 panels" in result or "3/6" in result, "Should show 3 panels generated"
    
    print("✅ StatusTrackerTool test passed!")
    return True

def test_retry_manager():
    """Test the RetryManagerTool"""
    print("\n🧪 Test 2: RetryManagerTool...")
    
    retry_tool = RetryManagerTool()
    
    # Test with failed panels
    result = retry_tool._run(
        failed_panels=[3, 5, 6],
        total_panels=6,
        current_attempt=1,
        max_retries=3
    )
    
    print(f"Retry Report:\n{result}")
    
    # Verify results
    assert "3 panels" in result or "Panels: 3" in result, "Should mention 3 failed panels"
    assert "Attempt 1" in result or "attempt 1" in result, "Should show current attempt"
    
    print("✅ RetryManagerTool test passed!")
    return True

def test_workflow_control():
    """Test the WorkflowControlTool"""
    print("\n🧪 Test 3: WorkflowControlTool...")
    
    workflow_tool = WorkflowControlTool()
    
    # Test check_status action
    result = workflow_tool._run(
        action="check_status",
        expected_panels=6
    )
    
    print(f"Workflow Status:\n{result[:200]}...")
    
    assert result is not None, "Workflow control should return a result"
    
    print("✅ WorkflowControlTool test passed!")
    return True

def test_panel_validation():
    """Test the PanelValidationTool"""
    print("\n🧪 Test 4: PanelValidationTool...")
    
    validation_tool = PanelValidationTool()
    
    # Test with panel mapping
    panel_map = {
        "1": "panel_001_test.png",
        "2": "panel_002_test.png",
        "3": "panel_003_test.png"
    }
    
    result = validation_tool._run(
        panel_map=panel_map,
        expected_panel_count=6
    )
    
    print(f"Validation Report:\n{result[:300]}...")
    
    # Verify results
    assert "VALIDATION REPORT" in result or "Panel" in result, "Should contain validation report"
    
    print("✅ PanelValidationTool test passed!")
    return True

def test_cleanup():
    """Test the CleanupTool"""
    print("\n🧪 Test 5: CleanupTool...")
    
    cleanup_tool = CleanupTool()
    
    # Test cleanup (dry run - won't actually delete files)
    result = cleanup_tool._run(
        target_folders=["temp_multi_character", "temp_refinement_images"],
        dry_run=True
    )
    
    print(f"Cleanup Report:\n{result}")
    
    assert "Cleanup" in result or "temp" in result.lower(), "Should mention cleanup or temp folders"
    
    print("✅ CleanupTool test passed!")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("🔧 Testing Orchestrator & Evaluator Tools")
    print("=" * 60)
    
    try:
        test_status_tracker()
        test_retry_manager()
        test_workflow_control()
        test_panel_validation()
        test_cleanup()
        
        print("\n" + "=" * 60)
        print("✨ All Orchestrator & Evaluator tests passed!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
