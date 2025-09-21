#!/usr/bin/env python3
"""
Simple test API to verify our path fix works in the web interface
"""
import os
import sys
sys.path.append('.')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import json
import time

app = FastAPI(title="Comic Book Creator API - Test Mode", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def test_image_generation(prompt: str):
    """Simulate the image generation process with our path fix"""
    # Simulate response from Gemini Image Tutorial server
    response_data = {
        "status": "success",
        "image_path": "output/server_generated_gemini-image-tutorial_17.png"  # Use the existing file
    }
    
    source_image_path = response_data["image_path"]
    print(f"[TEST] Original relative path: {source_image_path}")
    
    # Apply the same logic as in gemini_image_tool.py
    if not os.path.isabs(source_image_path):
        gemini_tutorial_dir = r"C:\Users\ninic\projects\Datacamp_projects\gemini-image-tutorial"
        source_image_path = os.path.join(gemini_tutorial_dir, source_image_path)
    
    print(f"[TEST] Resolved source path: {source_image_path}")
    
    # Check if source file exists
    if os.path.exists(source_image_path):
        return f"✅ Path fix working! Found image at: {source_image_path}"
    else:
        return f"❌ Path fix failed. Image not found at: {source_image_path}"

@app.get("/")
async def read_root():
    return {"message": "Comic Book Creator API Test Mode", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/generate_comic")
async def generate_comic_endpoint(prompt: str):
    """Test endpoint to verify path fix"""
    try:
        print(f"[TEST] Received prompt: {prompt}")
        
        def event_generator():
            yield f"data: {json.dumps({'type': 'status', 'message': 'Starting test comic generation...'})}\n\n"
            time.sleep(1)
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'Testing image path resolution...'})}\n\n"
            time.sleep(1)
            
            # Test our path fix
            result = test_image_generation(prompt)
            yield f"data: {json.dumps({'type': 'status', 'message': result})}\n\n"
            time.sleep(1)
            
            # Generate a simple test comic
            test_comic = f"""# Test Comic: {prompt}

## Panel 1
*Setting: A test scene*

**Description:** This is a test comic to verify that our path fix is working correctly.

![Test Image](images/comic_panels/server_generated_gemini-image-tutorial_17.png)

**Dialogue:** "The path fix is working!"

---

## Panel 2
*Setting: Success celebration*

**Description:** The image path has been successfully resolved and the file has been copied to the comic panels directory.

**Dialogue:** "🎉 Path resolution successful!"

---

**Status:** Path fix verification complete!
**Result:** {result}
"""
            
            yield f"data: {json.dumps({'type': 'comic', 'content': test_comic})}\n\n"
            yield f"data: {json.dumps({'type': 'complete', 'message': 'Test comic generation complete!'})}\n\n"
        
        return StreamingResponse(
            event_generator(), 
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        print(f"[TEST] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting Test API server...")
    print("Testing path fix for Gemini Image Tutorial integration...")
    print("Access the API at http://127.0.0.1:8002")
    uvicorn.run(app, host="127.0.0.1", port=8002)
