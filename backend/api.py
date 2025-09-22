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

# Mount static files for serving images
app.mount("/images", StaticFiles(directory="output"), name="images")

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
        crew = VisualComicCrew().crew()
        stream_callback(f"data: {json.dumps({'status': 'Crew initialized', 'details': f'{len(crew.agents)} agents / {len(crew.tasks)} tasks'})}\n\n")

        # Define a callback function to handle streaming output
        def on_task_complete(output: TaskOutput):
            stream_callback(f"data: {json.dumps({'status': 'Task Complete', 'details': output.description})}\n\n")

        # Attach the callback to each task
        for task in crew.tasks:
            task.callback = on_task_complete

        stream_callback(f"data: {json.dumps({'status': 'Starting Crew Execution...', 'details': None})}\n\n")
        stream_callback(f"data: {json.dumps({'status': 'Running crew kickoff', 'details': None})}\n\n")
        result = crew.kickoff(inputs=inputs)
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

        # Save the final result
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_filename = f"{sanitize_filename(topic)}.md"
        save_path = output_dir / output_filename
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        stream_callback(f"data: {json.dumps({'status': 'complete', 'markdown': markdown_content, 'file_path': str(save_path)})}\n\n")
    except Exception as e:
        stream_callback(f"data: {json.dumps({'status': 'error', 'details': str(e)})}\n\n")


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
