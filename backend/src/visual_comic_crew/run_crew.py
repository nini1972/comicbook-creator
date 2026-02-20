#!/usr/bin/env python
import sys
import warnings
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"DEBUG: Loaded environment variables from {env_path}")
except ImportError:
    print("DEBUG: python-dotenv not available, environment variables may not be loaded")

from datetime import datetime

from visual_comic_crew.crew import VisualComicCrew
from src.utils.comic_exporter import ComicExporter

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
        # Early check: detect whether any expected LLM / Generative API credentials are present.
        # This prevents long, hard-to-read tracebacks coming from underlying LLM libraries
        # (for example: litellm / Google Gemini) when a key is missing or None.
        expected_keys = [
            "GOOGLE_API_KEY",
            "GENAI_API_KEY",
            "GEMINI_API_KEY",
            "GOOGLE_APPLICATION_CREDENTIALS",
            "GOOGLE_GENERATIVE_API_KEY",
            "OPENAI_API_KEY",
            "LITELLM_API_KEY",
        ]
        found = [k for k in expected_keys if os.getenv(k)]
        if not found:
            print("ERROR: No LLM/Generative API credentials detected.")
            print("ERROR: Please set one of the following environment variables (or add it to your .env file):")
            print("  " + ", ".join(expected_keys))
            # Show a short sample of present environment variable keys to help debugging
            sample = [k for k in os.environ.keys() if any(token in k.upper() for token in ("API", "KEY", "GOOGLE", "OPENAI", "GEMINI"))]
            if sample:
                print("DEBUG: Detected environment keys (sample): " + ", ".join(sample[:20]))
            else:
                print("DEBUG: No obvious API-related environment variables found.")
            raise Exception("Missing LLM/Generative API credentials. Aborting early to avoid confusing tracebacks.")
        else:
            # For debugging, show a masked preview (first 3 chars) of any detected candidate keys
            previews = []
            for k in found:
                v = os.getenv(k) or ""
                masked = (v[:3] + "...") if len(v) >= 3 else (v + "...")
                previews.append(f"{k} prefix='{masked}'")
            print("DEBUG: Detected candidate API credentials (masked): " + ", ".join(previews))

        crew_instance = VisualComicCrew()
        print("DEBUG: VisualComicCrew instance created successfully")

        print("DEBUG: About to call crew().kickoff()")
        result = crew_instance.crew().kickoff(inputs=inputs)
        print(f"DEBUG: Crew execution completed. Result type: {type(result)}")
        print(f"DEBUG: Result attributes: {dir(result)}")

        # Additional debug output to confirm result handling
        markdown_output = None
        
        # Try different attributes to extract the output
        if hasattr(result, 'raw'):
            print(f"DEBUG: Using result.raw")
            markdown_output = result.raw
        elif hasattr(result, 'output'):
            print(f"DEBUG: Using result.output")
            markdown_output = result.output
        elif hasattr(result, 'final_output'):
            print(f"DEBUG: Using result.final_output")
            markdown_output = result.final_output
        elif hasattr(result, 'pydantic'):
            print(f"DEBUG: Using result.pydantic")
            markdown_output = str(result.pydantic)
        elif hasattr(result, 'json_dict'):
            print(f"DEBUG: Using result.json_dict")
            markdown_output = str(result.json_dict)
        elif isinstance(result, str):
            print(f"DEBUG: Result is already a string")
            markdown_output = result
        elif isinstance(result, (list, tuple)):
            print(f"DEBUG: Result is list/tuple, using last item")
            if result:
                markdown_output = str(result[-1])
        else:
            print(f"DEBUG: Converting result to string")
            markdown_output = str(result)
        
        print(f"DEBUG: Extracted markdown_output length: {len(markdown_output) if markdown_output else 0}")
        if markdown_output:
            print(f"DEBUG: First 200 chars: {markdown_output[:200]}")
        
        # Clean up agent status messages that shouldn't be in the final comic
        if markdown_output:
            # Remove the agent's completion message if present
            status_markers = [
                "Successfully generated complete comic",
                "Comic assembly marked as complete",
                "Story status updated to",
                "- 6 panels with",
                "- Properly embedded images",
                "- Clean markdown formatting",
                "PDF version generated",
                "Comic layout complete",
                "proper formatting",
                "embedded images"
            ]
            lines = markdown_output.split('\n')
            cleaned_lines = []
            skip_remaining = False
            
            for line in lines:
                # Check if this line starts the agent status message
                if any(marker in line for marker in status_markers):
                    skip_remaining = True
                    continue
                if not skip_remaining:
                    cleaned_lines.append(line)
            
            markdown_output = '\n'.join(cleaned_lines).strip()
            print(f"DEBUG: After cleaning, markdown length: {len(markdown_output)}")
        
        # If markdown_output is empty, try reading from the saved file
        if not markdown_output or len(markdown_output.strip()) == 0:
            print("DEBUG: Result was empty, trying to read from latest_comic.md")
            from src.utils.path_utils import get_backend_output_path
            latest_comic_path = Path(get_backend_output_path("")) / "latest_comic.md"
            if latest_comic_path.exists():
                try:
                    with open(latest_comic_path, 'r', encoding='utf-8') as f:
                        markdown_output = f.read()
                    print(f"DEBUG: Successfully read {len(markdown_output)} chars from latest_comic.md")
                except Exception as e:
                    print(f"DEBUG: Failed to read latest_comic.md: {e}")
            else:
                print(f"DEBUG: latest_comic.md not found at {latest_comic_path}")

        if markdown_output and len(markdown_output.strip()) > 0:
            print("\n" + "="*80)
            print("EXPORTING COMIC TO FILES...")
            print("="*80)
            
            # Create exporter and save files
            exporter = ComicExporter(topic=topic)
            
            # Save markdown file
            md_path = exporter.save_markdown(markdown_output)
            print(f"✅ Markdown saved to: {md_path}")
            
            # Generate PDF file
            try:
                pdf_path = exporter.generate_pdf(markdown_output, method="weasyprint")
                print(f"✅ PDF saved to: {pdf_path}")
            except Exception as pdf_error:
                print(f"⚠️ PDF generation failed: {pdf_error}")
                print("   (Markdown file was saved successfully)")
            
            print("="*80)
            print(f"COMIC EXPORT COMPLETE!")
            print("="*80 + "\n")
        else:
            print("⚠️ Warning: Could not extract markdown output from result. Files not saved.")

    except Exception as e:
        print(f"DEBUG: Exception occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        # Show which of the expected candidate keys were present (masked) to help identify which key the run used for testing
        try:
            set_keys = [k for k in expected_keys if os.getenv(k)]
            if set_keys:
                previews = []
                for k in set_keys:
                    v = os.getenv(k) or ""
                    masked = (v[:3] + "...") if len(v) >= 3 else (v + "...")
                    previews.append(f"{k} prefix='{masked}'")
                print("DEBUG: Candidate API keys present (masked): " + ", ".join(previews))
            else:
                print("DEBUG: No expected candidate API keys were set in the environment at exception time.")
        except Exception:
            # Be very careful not to raise while handling the original exception
            print("DEBUG: Failed to compute masked API key previews.")
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
