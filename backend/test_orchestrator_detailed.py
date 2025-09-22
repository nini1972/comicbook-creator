#!/usr/bin/env python3
"""
Comprehensive test of the orchestrator system with detailed logging
This will show exactly what's happening behind the scenes
"""

import sys
import os
sys.path.append('src')

from visual_comic_crew.crew import VisualComicCrew

def test_orchestrator_detailed():
    """Test orchestrator system with detailed behind-the-scenes logging"""
    print("🔍 DETAILED ORCHESTRATOR SYSTEM TEST")
    print("=" * 60)
    print("This test will show exactly what happens behind the scenes...")
    
    try:
        # Create crew instance
        print("\n1. 🏗️ Creating VisualComicCrew instance...")
        crew_instance = VisualComicCrew()
        print("   ✅ Crew instance created")
        
        # Get the crew
        crew = crew_instance.crew()
        print(f"   ✅ Crew object created with {len(crew.agents)} agents and {len(crew.tasks)} tasks")
        
        # Show agent details
        print("\n2. 👥 Agent Configuration:")
        for i, agent in enumerate(crew.agents):
            print(f"   {i+1}. {agent.role}")
            if hasattr(agent, 'tools') and agent.tools:
                print(f"      🔧 Tools: {[tool.__class__.__name__ for tool in agent.tools]}")
            else:
                print(f"      🔧 Tools: None")
        
        # Show task details
        print("\n3. 📋 Task Configuration:")
        for i, task in enumerate(crew.tasks):
            print(f"   {i+1}. {task.description[:50]}...")
            if hasattr(task, 'context') and task.context:
                context_names = [ctx.description[:30] + "..." for ctx in task.context]
                print(f"      🔗 Context: {context_names}")
        
        # Test inputs
        inputs = {
            'topic': 'a friendly robot helping a child with homework',
            'style': 'cartoon',
            'panels': 3
        }
        
        print(f"\n4. 🎬 Test Inputs:")
        print(f"   Topic: {inputs['topic']}")
        print(f"   Style: {inputs['style']}")
        print(f"   Panels: {inputs['panels']}")
        
        print(f"\n5. 🚀 Starting orchestrated workflow execution...")
        print("   (This will show the actual agent interactions...)")
        
        # Run with verbose output
        result = crew.kickoff(inputs=inputs)
        
        print("\n6. 📊 Execution Results:")
        print(f"   Result type: {type(result)}")
        
        if result:
            print(f"   ✅ Workflow completed")
            if hasattr(result, 'raw'):
                result_str = str(result.raw)
                print(f"   📄 Result length: {len(result_str)} characters")
                
                # Show first 500 characters of result
                if len(result_str) > 500:
                    print(f"   📝 Result preview: {result_str[:500]}...")
                else:
                    print(f"   📝 Result: {result_str}")
            
            # Check if there are task outputs
            if hasattr(result, 'tasks_output') and result.tasks_output:
                print(f"   📋 Task outputs: {len(result.tasks_output)} tasks completed")
                for i, task_output in enumerate(result.tasks_output):
                    print(f"      Task {i+1}: {str(task_output)[:100]}...")
        else:
            print("   ⚠️ No result returned")
            
    except Exception as e:
        print(f"❌ ERROR during orchestrator test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("Starting comprehensive orchestrator test...")
    success = test_orchestrator_detailed()
    
    if success:
        print("\n🎉 Orchestrator test completed!")
    else:
        print("\n❌ Orchestrator test failed!")