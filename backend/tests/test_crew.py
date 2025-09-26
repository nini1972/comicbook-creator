#!/usr/bin/env python3
"""
Simple test script to run the VisualComicCrew directly.
"""
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.visual_comic_crew.crew import VisualComicCrew

def main():
    topic = "a cat chasing a laser pointer"

    print(f"Testing comic generation for topic: '{topic}'")

    try:
        # Initialize the crew
        print("Initializing crew...")
        crew_instance = VisualComicCrew().crew()

        # Run the crew
        print("Starting crew execution...")
        inputs = {'topic': topic}
        result = crew_instance.kickoff(inputs=inputs)

        print("Crew execution completed!")
        print(f"Result type: {type(result)}")

        # Extract the content
        if hasattr(result, 'final_output'):
            content = result.final_output
        elif hasattr(result, 'output'):
            content = result.output
        elif isinstance(result, str):
            content = result
        else:
            content = str(result)

        print(f"Generated content length: {len(content)} characters")
        print("\n--- Generated Content ---")
        print(content[:500] + "..." if len(content) > 500 else content)

        # Save to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{topic.replace(' ', '_')}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\nContent saved to: {output_file}")

    except Exception as e:
        print(f"Error during crew execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()