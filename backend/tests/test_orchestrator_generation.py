#!/usr/bin/env python3
"""
Test orchestrator with actual comic generation - behind the scenes view
"""
import sys
import os
sys.path.append('src')

from visual_comic_crew.crew import VisualComicCrew

def test_orchestrator_with_generation():
    """Test orchestrator with actual comic generation"""
    print("🎬 ORCHESTRATOR COMIC GENERATION TEST")
    print("=" * 50)
    print("This will run the actual orchestrator workflow...")
    
    try:
        # Create crew
        print("1. 🏗️ Creating crew...")
        crew_instance = VisualComicCrew()
        crew = crew_instance.crew()
        print(f"   ✅ Crew ready with {len(crew.agents)} agents")
        
        # Simple test case
        inputs = {
            'topic': 'a cat discovering a magical box',
            'style': 'cartoon',
            'panels': 3
        }
        
        print(f"\n2. 🎯 Test Comic:")
        print(f"   Topic: {inputs['topic']}")
        print(f"   Style: {inputs['style']}")
        print(f"   Panels: {inputs['panels']}")
        
        print(f"\n3. 🚀 Starting orchestrated workflow...")
        print("   (Watch for orchestrator coordination and retry logic)")
        print("   " + "="*45)
        
        # Execute the workflow
        result = crew.kickoff(inputs=inputs)
        
        print("\n" + "="*45)
        print("4. 📊 Workflow Results:")
        
        if result:
            print("   ✅ Workflow completed successfully!")
            
            # Show result details
            if hasattr(result, 'raw'):
                result_text = str(result.raw)
                print(f"   📄 Result length: {len(result_text)} characters")
                
                # Look for specific orchestrator outputs
                if "orchestrat" in result_text.lower():
                    print("   🎯 Orchestrator output detected in results")
                
                if "retry" in result_text.lower():
                    print("   🔄 Retry logic mentioned in results")
                
                if "panel" in result_text.lower():
                    print("   🖼️ Panel information found in results")
                
                # Show a sample of the output
                print(f"\n   📝 Result sample:")
                lines = result_text.split('\n')
                for i, line in enumerate(lines[:10]):  # Show first 10 lines
                    if line.strip():
                        print(f"      {line.strip()}")
                
                if len(lines) > 10:
                    print(f"      ... ({len(lines)-10} more lines)")
            
            # Check task outputs if available
            if hasattr(result, 'tasks_output'):
                print(f"\n   📋 Task outputs: {len(result.tasks_output)} tasks")
                for i, task_output in enumerate(result.tasks_output):
                    task_str = str(task_output)
                    print(f"      Task {i+1}: {task_str[:80]}...")
        else:
            print("   ⚠️ No result returned from workflow")
        
        print(f"\n🎉 Orchestrator test completed!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_orchestrator_with_generation()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")