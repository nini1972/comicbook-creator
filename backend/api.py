import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import re
import os
import sys
from pathlib import Path
from src.visual_comic_crew.crew import VisualComicCrew
from crewai.tasks.task_output import TaskOutput

# Import ComicExporter - it's in backend/src/utils/comic_exporter.py
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))

# Now import ComicExporter
from src.utils.comic_exporter import ComicExporter

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"DEBUG: Loaded environment variables from {env_path}")
except ImportError:
    print("DEBUG: python-dotenv not available, environment variables may not be loaded")


# Add the backend directory to the Python path to allow for package imports
sys.path.append(str(Path(__file__).resolve().parent))

# --- FastAPI Application ---
app = FastAPI(
    title="Comic Book Creator API",
    description="An API to generate comic books using a CrewAI process. Provides a streaming endpoint for real-time updates.",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://192.168.1.10:3002",
    "http://localhost:3003",
    "http://192.168.1.10:3003",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files for serving images (always from project_root/frontend/public/comic_panels)
project_root = Path(__file__).parent.parent
frontend_comic_panels = project_root / "frontend" / "public" / "comic_panels"
frontend_comic_panels.mkdir(parents=True, exist_ok=True)
app.mount("/comic_panels", StaticFiles(directory=str(frontend_comic_panels)), name="comic_panels")

def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be a valid filename."""
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9_]+', '', name.replace(' ', '_'))
    return name[:50]

async def run_crew_stream(topic: str, stream_callback):
    """
    Runs the CrewAI process and uses a callback to stream status updates.
    """
    try:
        inputs = {'topic': topic}
        stream_callback(f"data: {json.dumps({'status': 'Initializing crew objects', 'details': None})}\n\n")
        print("DEBUG: About to create VisualComicCrew instance")
        crew = VisualComicCrew()
        print("DEBUG: VisualComicCrew instance created successfully")
        stream_callback(f"data: {json.dumps({'status': 'Crew initialized', 'details': f'CrewBase instance created'})}\n\n")

        stream_callback(f"data: {json.dumps({'status': 'Starting Crew Execution...', 'details': None})}\n\n")
        stream_callback(f"data: {json.dumps({'status': 'Running crew kickoff', 'details': None})}\n\n")
        # The CrewBase-decorated class exposes a `crew()` method that returns the Crew instance.
        # Call kickoff on that Crew instance to execute the workflow.
        stream_callback(f"data: {json.dumps({'status': 'Calling crew().kickoff', 'details': None})}\n\n")
        print("DEBUG: About to call crew().kickoff()")
        try:
            result = crew.crew().kickoff(inputs=inputs)
            print("DEBUG: crew().kickoff() completed")
        except Exception as e:
            err_text = str(e)
            print(f"DEBUG: Exception in crew().kickoff(): {err_text}")
            stream_callback(f"data: {json.dumps({'status': 'error', 'details': err_text})}\n\n")
            # If it's an Anthropic model-not-found error, attempt a one-time fallback to OpenAI GPT-4o
            if 'claude-sonnet-4' in err_text or 'AnthropicException' in err_text or 'model: claude' in err_text:
                try:
                    stream_callback(f"data: {json.dumps({'status': 'info', 'details': 'Detected Anthropic model error; retrying with fallback LLMs (openai/gpt-4o)'})}\n\n")
                    # Replace anthropic/claude entries in the crew's agents_config
                    for k, v in crew.agents_config.items():
                        if isinstance(v, dict) and 'llm' in v and isinstance(v['llm'], str) and ('anthropic' in v['llm'].lower() or 'claude' in v['llm'].lower()):
                            v['llm'] = 'openai/gpt-4o'
                    stream_callback(f"data: {json.dumps({'status': 'info', 'details': 'Retrying kickoff with updated agent LLMs'})}\n\n")
                    try:
                        result = crew.crew().kickoff(inputs=inputs)
                    except Exception as e2:
                        stream_callback(f"data: {json.dumps({'status': 'error', 'details': f'Retry failed: {e2}'})}\n\n")
                        return
                except Exception:
                    return
            else:
                return
        # Debug: describe result type
        result_type = type(result).__name__
        stream_callback(f"data: {json.dumps({'status': 'Crew execution finished', 'details': f'Result type: {result_type}'})}\n\n")

        def _extract(res):
            try:
                if isinstance(res, str):
                    return res.strip()
                # Common CrewAI result object attributes
                for attr in ('final_output', 'output', 'raw', 'result'):
                    if hasattr(res, attr):
                        val = getattr(res, attr)
                        if isinstance(val, str):
                            return val
                # If it's iterable (list of task outputs)
                if isinstance(res, (list, tuple)):
                    collected = []
                    for r in res:
                        extracted = _extract(r)
                        if extracted:
                            collected.append(extracted)
                    return '\n\n'.join(collected)
            except Exception as ie:  # inner extraction error
                return f"(Extraction error: {ie})"
            return str(res)

        markdown_content = _extract(result) or "(No content produced)"
        stream_callback(f"data: {json.dumps({'status': 'Crew execution finished', 'details': f'Extracted length: {len(markdown_content)} chars'})}\n\n")
        # Debug: print final markdown content
        print(f"[DEBUG] Final markdown:\n{markdown_content}")
        
    except Exception as outer_e:
        stream_callback(f"data: {json.dumps({'status': 'error', 'details': f'Outer exception: {outer_e}'})}\n\n")
        return

    # Save the final result
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_filename = f"{sanitize_filename(topic)}.md"
    save_path = output_dir / output_filename
    safe_topic = sanitize_filename(topic)
    exporter = ComicExporter(safe_topic)
    save_path = exporter.save_markdown(markdown_content)
    exporter.generate_pdf(markdown_content)

    stream_callback(f"data: {json.dumps({'status': 'complete', 'markdown': markdown_content, 'file_path': str(save_path)})}\n\n")


@app.get("/generate-comic/")
async def generate_comic(request: Request, topic: str = "A cat who wants to fly"):
    """
    Endpoint to generate a comic. It streams the progress of the CrewAI agents.
    """
    async def event_generator():
        # A queue to hold messages from the crew callback
        message_queue = asyncio.Queue()

        def stream_callback(message):
            message_queue.put_nowait(message)

        # Run the crew in a background task 
        asyncio.create_task(run_crew_stream(topic, stream_callback))

        # Yield messages from the queue as they arrive
        while True:
            message = await message_queue.get()
            yield message
            if '"status": "complete"' in message or '"status": "error"' in message:
                break
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")




   
# --- Main entry point to run the server ---
if __name__ == "__main__":
    print("Starting Comic Book Creator API Server...")
    print("Access the API at http://127.0.0.1:8002")
    uvicorn.run(app, host="127.0.0.1", port=8002)