#!/usr/bin/env python3
"""
Direct crew test - tests the crew without API server
"""
import sys
import os
import time

# Add the src directory to the Python path
sys.path.append('src')

def test_direct_crew():
    """Test the crew directly without API server"""
    print("=" * 70)
    print("DIRECT CREW WORKFLOW TEST")
    print("=" * 70)
    
    test_prompt = "Create a short comic about a brave little mouse discovering magical cheese"
    print(f"Test Prompt: {test_prompt}")
    print()
    
    try:
        # Import the crew
        from visual_comic_crew.crew import VisualComicCrew
        
        print("✓ CrewAI modules imported successfully")
        
        # Create crew instance
        crew_instance = VisualComicCrew()
        crew = crew_instance.crew()
        
        print(f"✓ Crew created with {len(crew.agents)} agents and {len(crew.tasks)} tasks")
        
        # List the agents
        print("\nCrew agents:")
        for i, agent in enumerate(crew.agents, 1):
            print(f"  {i}. {agent.role}")
        
        print(f"\n{'='*50}")
        print("STARTING COMIC CREATION...")
        print(f"{'='*50}")
        
        start_time = time.time()
        
        # Run the crew
        inputs = {'topic': test_prompt}
        result = crew.kickoff(inputs=inputs)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n{'='*50}")
        print("WORKFLOW COMPLETED!")
        print(f"{'='*50}")
        print(f"Execution time: {execution_time:.2f} seconds")
        
        # Show result
        if hasattr(result, 'raw'):
            result_text = str(result.raw)
        else:
            result_text = str(result)
            
        print(f"\nResult length: {len(result_text)} characters")
        print(f"\nFirst 500 characters:")
        print("-" * 50)
        print(result_text[:500])
        if len(result_text) > 500:
            print("... [truncated]")
        print("-" * 50)
        
        # Check for generated images
        output_dir = "output/comic_panels"
        if os.path.exists(output_dir):
            image_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
            print(f"\n✓ Images found: {len(image_files)}")
            for img in image_files[-3:]:
                print(f"  - {img}")
        else:
            print(f"\n⚠ No comic_panels directory found at {output_dir}")
        
        # Check for comic files
        main_output_dir = "output"
        if os.path.exists(main_output_dir):
            comic_files = [f for f in os.listdir(main_output_dir) if f.endswith('.md')]
            print(f"\n✓ Comic files: {len(comic_files)}")
            for comic in comic_files[-3:]:
                print(f"  - {comic}")
        
        print(f"\n{'='*50}")
        print("SUMMARY")
        print(f"{'='*50}")
        print(f"✓ Execution time: {execution_time:.2f}s")
        print(f"✓ Result size: {len(result_text)} characters")
        
        return True
        
    except Exception as e:
        print(f"\n❌ WORKFLOW FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_crew()
    if success:
        print(f"\n🎉 DIRECT CREW TEST COMPLETED SUCCESSFULLY!")
    else:
        print(f"\n💥 DIRECT CREW TEST FAILED!")