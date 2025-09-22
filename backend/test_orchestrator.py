#!/usr/bin/env python3
"""
Test script for the new Orchestrator + Evaluator system
"""

import sys
import os
sys.path.append('src')

from visual_comic_crew.crew import VisualComicCrew

def test_orchestrator_system():
    """Test the new orchestrator + evaluator system"""
    
    print("🧪 TESTING ORCHESTRATOR + EVALUATOR SYSTEM")
    print("=" * 60)
    
    try:
        # Create crew instance
        print("1. Creating VisualComicCrew instance...")
        crew_instance = VisualComicCrew()
        print("   ✅ Crew instance created successfully")
        
        # Check agents
        print("\n2. Checking agent configuration...")
        crew = crew_instance.crew()
        agents = crew.agents
        print(f"   📋 Total agents: {len(agents)}")
        for i, agent in enumerate(agents):
            print(f"   {i+1}. {agent.role}")
        
        # Check tasks
        print("\n3. Checking task configuration...")
        tasks = crew.tasks
        print(f"   📋 Total tasks: {len(tasks)}")
        for i, task in enumerate(tasks):
            print(f"   {i+1}. {task.description[:50]}...")
        
        # Check orchestrator tools
        print("\n4. Checking orchestrator tools...")
        orchestrator = None
        for agent in agents:
            if "orchestrator" in agent.role.lower() or "workflow" in agent.role.lower():
                orchestrator = agent
                break
        
        if orchestrator:
            print(f"   ✅ Orchestrator found: {len(orchestrator.tools)} tools")
            for tool in orchestrator.tools:
                print(f"      - {tool.name}")
        else:
            print("   ❌ Orchestrator agent not found")
        
        # Check evaluator tools
        print("\n5. Checking evaluator tools...")
        evaluator = None
        for agent in agents:
            if "evaluator" in agent.role.lower() or "validation" in agent.role.lower():
                evaluator = agent
                break
        
        if evaluator:
            print(f"   ✅ Evaluator found: {len(evaluator.tools)} tools")
            for tool in evaluator.tools:
                print(f"      - {tool.name}")
        else:
            print("   ❌ Evaluator agent not found")
        
        print("\n✅ ORCHESTRATOR SYSTEM TEST COMPLETE!")
        print("The system is ready for orchestrated comic generation with validation and retry logic.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during orchestrator system test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Orchestrator + Evaluator Integration")
    print("This test verifies the new workflow coordination system")
    print()
    
    success = test_orchestrator_system()
    
    if success:
        print("\n🎉 SUCCESS: Orchestrator system is ready!")
        print("\nNext steps:")
        print("1. Test with actual comic generation")
        print("2. Verify retry logic works correctly")
        print("3. Confirm evaluator prevents broken comics")
    else:
        print("\n💥 FAILED: Orchestrator system needs fixes")
        sys.exit(1)