import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import re
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path to allow for package imports
sys.path.append(str(Path(__file__).resolve().parent))

# --- FastAPI Application ---
app = FastAPI(
    title="Comic Book Creator API",
    description="An API to generate comic books using a CrewAI process. Provides a streaming endpoint for real-time updates.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be a valid filename."""
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9_]+', '', name.replace(' ', '_'))
    return name[:50]  # Limit length

async def run_crew_stream(topic: str):
    """
    Runs the CrewAI process and yields status updates.
    """
    yield f"data: {json.dumps({'status': 'Initializing Crew...', 'details': None})}\n\n"
    await asyncio.sleep(1)

    # This is a placeholder for the actual crew execution.
    # In the next steps, we will replace this with the real logic
    # that calls your VisualComicCrew and yields its progress.
    try:
        yield f"data: {json.dumps({'status': 'Starting story creation...', 'details': 'Agent: Story Writer'})}\n\n"
        await asyncio.sleep(5) # Simulate work

        yield f"data: {json.dumps({'status': 'Generating visuals...', 'details': 'Agent: Visual Director'})}\n\n"
        await asyncio.sleep(5) # Simulate work

        yield f"data: {json.dumps({'status': 'Assembling comic...', 'details': 'Agent: Comic Assembler'})}\n\n"
        await asyncio.sleep(3) # Simulate work
        
        # Simulate creating the final file
        sanitized_topic = sanitize_filename(topic)
        output_filename = f"output/{sanitized_topic}.md"
        
        # In a real scenario, this would be the actual markdown content
        final_markdown = f"# Comic: {topic}\n\nThis is the generated comic strip for '{topic}'.\n\n![Panel 1](placeholder.jpg)"

        # We will save the file in the backend later
        # For now, we just send the content to the frontend
        
        yield f"data: {json.dumps({'status': 'complete', 'markdown': final_markdown})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'status': 'error', 'details': str(e)})}\n\n"


@app.get("/generate-comic/")
async def generate_comic(request: Request, topic: str = "A cat who wants to fly"):
    """
    Endpoint to generate a comic. It streams the progress of the CrewAI agents.
    """
    return StreamingResponse(run_crew_stream(topic), media_type="text/event-stream")

# --- Main entry point to run the server ---
if __name__ == "__main__":
    print("Starting Comic Book Creator API Server...")
    print("Access the API at http://127.0.0.1:8000")
    print("Try the streaming endpoint: http://127.0.0.1:8000/generate-comic/?topic=my_awesome_comic")
    uvicorn.run(app, host="127.0.0.1", port=8000)
