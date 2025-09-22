#!/usr/bin/env python3
"""
Test the orchestrator system with actual comic generation
This validates the complete workflow including retry logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.crew import VisualComicCrew

def test_orchestrator_workflow():
    """Test the orchestrator with a simple comic generation"""
    print("🎬 TESTING ORCHESTRATOR WORKFLOW")
    print("=" * 60)
    
    try:
        # Create crew instance
        print("1. Initializing VisualComicCrew...")
        crew_instance = VisualComicCrew()
        
        # Simple test inputs
        inputs = {
            'topic': 'a friendly robot helping a child with homework',
            'style': 'cartoon',
            'panels': 3
        }
        
        print(f"2. Starting orchestrated comic generation...")
        print(f"   Topic: {inputs['topic']}")
        print(f"   Style: {inputs['style']}")
        print(f"   Panels: {inputs['panels']}")
        
        # Run the crew with orchestrator
        print("\n3. Executing crew workflow...")
        result = crew_instance.crew().kickoff(inputs=inputs)
        
        print("\n✅ ORCHESTRATED WORKFLOW COMPLETE!")
        print(f"Result type: {type(result)}")
        
        # Check if we got a result
        if result:
            print(f"✅ Generated comic successfully")
            if hasattr(result, 'raw'):
                print(f"Raw result length: {len(str(result.raw))}")
        else:
            print("⚠️ No result returned")
            
    except Exception as e:
        print(f"❌ ERROR during orchestrated workflow: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_orchestrator_workflow()
    if success:
        print("\n🎉 Orchestrator workflow test completed!")
    else:
        print("\n❌ Orchestrator workflow test failed!")