#!/usr/bin/env python
"""
Full end-to-end test of the comic generation workflow with Evaluator/Orchestrator
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.visual_comic_crew.crew import VisualComicCrew

def test_full_comic_generation(topic: str = None):
    """Run a full comic generation with a simple test topic"""
    
    print("=" * 80)
    print("🚀 FULL COMIC GENERATION TEST")
    print("=" * 80)
    
    # Use topic from argument, env var, or default
    test_topic = topic or os.environ.get("COMIC_TOPIC") or "A brave cat who wants to fly"
    
    print(f"\n📖 Topic: {test_topic}")
    print("\n⚙️  This will test the complete workflow:")
    print("   1. Story Writer creates narrative")
    print("   2. Visual Director plans panels")
    print("   3. Orchestrator manages generation workflow")
    print("   4. Evaluator validates outputs")
    print("   5. Comic Assembler creates final product")
    print("\n" + "=" * 80)
    
    inputs = {'topic': test_topic}
    
    try:
        print("\n🔧 Creating VisualComicCrew instance...")
        crew_instance = VisualComicCrew()
        print("✅ Crew instance created")
        
        print("\n🎬 Starting crew execution...")
        print("-" * 80)
        result = crew_instance.crew().kickoff(inputs=inputs)
        print("-" * 80)
        
        print("\n✨ COMIC GENERATION COMPLETED!")
        print("=" * 80)
        print(f"\n📊 Result:\n{result}")
        print("\n" + "=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # Accept optional topic as first command-line argument
    # Usage: uv run python tests/test_full_run.py "My new topic"
    cli_topic = sys.argv[1] if len(sys.argv) > 1 else None
    exit_code = test_full_comic_generation(topic=cli_topic)
    sys.exit(exit_code)
