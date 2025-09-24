#!/usr/bin/env python3
"""
Quick orchestrator test to see the system in action
"""
import sys
import os
sys.path.append('src')

print("🔍 QUICK ORCHESTRATOR TEST")
print("=" * 40)

try:
    # Test basic imports
    print("1. Testing imports...")
    from visual_comic_crew.crew import VisualComicCrew
    print("   ✅ VisualComicCrew imported successfully")
    
    # Create crew
    print("2. Creating crew instance...")
    crew_instance = VisualComicCrew()
    print("   ✅ Crew instance created")
    
    # Get crew details
    crew = crew_instance.crew()
    print(f"   ✅ Crew has {len(crew.agents)} agents and {len(crew.tasks)} tasks")
    
    # Show orchestrator details
    print("3. Checking orchestrator configuration...")
    orchestrator_agent = None
    for agent in crew.agents:
        if "orchestrat" in agent.role.lower() or "workflow" in agent.role.lower():
            orchestrator_agent = agent
            break
    
    if orchestrator_agent:
        print(f"   ✅ Orchestrator found: {orchestrator_agent.role}")
        if hasattr(orchestrator_agent, 'tools') and orchestrator_agent.tools:
            tool_names = [tool.__class__.__name__ for tool in orchestrator_agent.tools]
            print(f"   🔧 Orchestrator tools: {tool_names}")
        else:
            print("   ⚠️ Orchestrator has no tools")
    else:
        print("   ❌ Orchestrator agent not found")
    
    # Check orchestration task
    print("4. Checking orchestration task...")
    orchestration_task = None
    for task in crew.tasks:
        if "orchestrat" in task.description.lower():
            orchestration_task = task
            break
    
    if orchestration_task:
        print("   ✅ Orchestration task found")
        print(f"   📝 Task description preview: {orchestration_task.description[:100]}...")
    else:
        print("   ❌ Orchestration task not found")
    
    print("\n🎉 Quick test completed!")
    print("The orchestrator system appears to be properly configured.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()