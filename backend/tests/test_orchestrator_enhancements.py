#!/usr/bin/env python3
"""
Test the enhanced orchestrator tools with registry and sync integration
"""
import sys
import os
sys.path.append('src')

from visual_comic_crew.tools.orchestrator_tools import WorkflowControlTool, RetryManagerTool
from visual_comic_crew.tools.registry import update_registry_entry, read_registry, get_panel_status

def test_orchestrator_enhancements():
    """Test the enhanced orchestrator tools with registry integration"""
    print("🧪 TESTING ENHANCED ORCHESTRATOR TOOLS")
    print("=" * 60)
    
    try:
        # Setup: Create some registry entries to simulate previous generation
        print("1. 🏗️ Setting up test registry state...")
        update_registry_entry("panel_1", True, True, True)   # Verified
        update_registry_entry("panel_2", True, False, False)  # Backend only
        update_registry_entry("panel_3", False, False, False) # Missing
        
        registry = read_registry()
        print(f"   Registry setup complete: {len(registry)} entries")
        for panel_id, status in registry.items():
            print(f"   - {panel_id}: verified={status.get('verified')}")
        
        # Test 1: WorkflowControlTool status check with sync polling
        print("\n2. 🔍 Testing WorkflowControlTool status check...")
        workflow_tool = WorkflowControlTool()
        status_result = workflow_tool._run(action="check_status")
        
        print("   Status check result:")
        print("   " + status_result.replace('\n', '\n   '))
        
        # Test 2: RetryManagerTool with registry filtering
        print("\n3. 🔄 Testing RetryManagerTool with registry filtering...")
        retry_tool = RetryManagerTool()
        
        # Simulate failed panels including some that are now verified
        failed_panels = [1, 2, 3, 4, 5]  # Panel 1 should be filtered out as verified
        
        print(f"   Input failed panels: {failed_panels}")
        print("   Expected: Panel 1 should be filtered out (verified in registry)")
        
        retry_result = retry_tool._run(
            failed_panels=failed_panels,
            total_panels=6,
            current_attempt=1,
            max_retries=3
        )
        
        print("   Retry management result:")
        print("   " + retry_result.replace('\n', '\n   '))
        
        # Test 3: Verify registry filtering logic directly
        print("\n4. 🧠 Testing registry filtering logic...")
        filtered_panels = []
        verified_panels = []
        
        for panel_num in failed_panels:
            panel_id = f"panel_{panel_num}"
            status = get_panel_status(panel_id)
            if not status.get('verified'):
                filtered_panels.append(panel_num)
            else:
                verified_panels.append(panel_num)
        
        print(f"   Original failed panels: {failed_panels}")
        print(f"   Registry-verified panels: {verified_panels}")
        print(f"   Actual panels needing retry: {filtered_panels}")
        
        # Verify results
        expected_verified = [1]  # Only panel 1 is marked as verified
        expected_retry = [2, 3, 4, 5]  # These should still need retry
        
        success = (verified_panels == expected_verified and 
                  filtered_panels == expected_retry)
        
        if success:
            print("   ✅ Registry filtering working correctly!")
        else:
            print("   ❌ Registry filtering results unexpected")
            print(f"      Expected verified: {expected_verified}, got: {verified_panels}")
            print(f"      Expected retry: {expected_retry}, got: {filtered_panels}")
        
        print("\n5. 📚 Final registry state:")
        final_registry = read_registry()
        for panel_id, status in final_registry.items():
            print(f"   - {panel_id}: backend={status.get('backend_synced')}, frontend={status.get('frontend_synced')}, verified={status.get('verified')}")
        
        print("\n✅ Enhanced orchestrator tools test completed!")
        return success
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_orchestrator_enhancements()
    if success:
        print("\n🎉 All orchestrator enhancement tests passed!")
    else:
        print("\n❌ Some tests failed!")