#!/usr/bin/env python
import sys
import warnings
import os

from datetime import datetime

from visual_comic_crew.crew import VisualComicCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def get_topic():
    print("DEBUG: Starting get_topic() function")
    # Read from user_preference.txt for default
    pref_file = os.path.join(os.path.dirname(__file__), '..', '..', 'knowledge', 'user_preference.txt')
    default_topic = "AI Agents Adventures"
    if os.path.exists(pref_file):
        with open(pref_file, 'r') as f:
            content = f.read()
            if "interested in" in content:
                default_topic = content.split("interested in")[1].split(".")[0].strip()
    
    print(f"DEBUG: Default topic set to: {default_topic}")
    # Check if running in interactive mode
    try:
        topic = input(f"Enter comic topic (default: {default_topic}): ").strip()
        print(f"DEBUG: User input topic: '{topic}'")
        return topic if topic else default_topic
    except EOFError:
        # Non-interactive mode, use default
        print(f"DEBUG: Non-interactive mode detected. Using default topic: {default_topic}")
        return default_topic

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    print("DEBUG: Starting run() function")
    topic = get_topic()
    print(f"DEBUG: Topic selected: {topic}")
    
    inputs = {
        'topic': topic
    }
    print(f"DEBUG: Inputs prepared: {inputs}")
    
    try:
        print("DEBUG: About to create VisualComicCrew instance")
        crew_instance = VisualComicCrew()
        print("DEBUG: VisualComicCrew instance created successfully")
        
        print("DEBUG: About to call crew().kickoff()")
        result = crew_instance.crew().kickoff(inputs=inputs)
        print(f"DEBUG: Crew execution completed. Result: {result}")
        
    except Exception as e:
        print(f"DEBUG: Exception occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    topic = get_topic()
    inputs = {
        "topic": topic
    }
    try:
        VisualComicCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        VisualComicCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    topic = get_topic()
    inputs = {
        "topic": topic
    }
    
    try:
        VisualComicCrew().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
