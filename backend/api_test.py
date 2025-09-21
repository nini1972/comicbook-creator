import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json

# --- FastAPI Application ---
app = FastAPI(
    title="Comic Book Creator API",
    description="An API to generate comic books using a CrewAI process. Provides a streaming endpoint for real-time updates.",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",
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

@app.get("/")
async def root():
    return {"message": "Comic Book Creator API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is healthy"}

@app.get("/generate-comic/")
async def generate_comic_placeholder(request: Request, topic: str = "A cat who wants to fly"):
    """
    Placeholder endpoint to test the API without CrewAI dependencies.
    """
    async def event_generator():
        yield f"data: {json.dumps({'status': 'starting', 'details': f'Topic: {topic}'})}\n\n"
        await asyncio.sleep(1)
        yield f"data: {json.dumps({'status': 'processing', 'details': 'This is a placeholder response'})}\n\n"
        await asyncio.sleep(1)
        yield f"data: {json.dumps({'status': 'complete', 'markdown': '# Test Comic\\n\\nThis is a test comic about: ' + topic, 'file_path': 'test.md'})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- Main entry point to run the server ---
if __name__ == "__main__":
    print("Starting Comic Book Creator API Server (Test Mode)...")
    print("Access the API at http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)
