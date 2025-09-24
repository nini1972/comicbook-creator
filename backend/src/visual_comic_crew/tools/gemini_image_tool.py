from crewai.tools import BaseTool
import requests
from typing import Type, Optional, List
from pydantic import BaseModel, Field
import os
import time
import shutil
import re
from pathlib import Path

# Simple helper for debug prints (could be replaced with logging module later)
def _dbg(msg: str):
    print(f"[GeminiImageTool] {msg}")

class GeminiImageToolSchema(BaseModel):
    """Input for GeminiImageTool."""
    prompt: str = Field(..., description="The detailed prompt for image generation. The prompt should refer to the panel number and include all relevant details.")
    base_image_paths: Optional[List[str]] = Field(None, description="Optional list of local file paths for base images to be used as reference.")

class GeminiImageTool(BaseTool):
    name: str = "Gemini Image Generator"
    description: str = (
        "Generates a comic panel image using the local image server (Gemini Flash). "
        "Provide a detailed prompt including panel number, characters, style, perspective, and mood."
    )
    args_schema: Type[BaseModel] = GeminiImageToolSchema
    # Allow override via environment variable GEMINI_IMAGE_SERVER_URL
    server_url: str = os.getenv("GEMINI_IMAGE_SERVER_URL", "http://127.0.0.1:8000/generate-image/")

    def _run(self, prompt: str, base_image_paths: Optional[List[str]] = None) -> str:
        """Generate an image and return the saved path or an error string."""
        # Explicit validation to catch common errors
        if not isinstance(prompt, str):
            return f"Error: Prompt must be a string, got {type(prompt).__name__}: {prompt}"
        
        if len(prompt.strip()) == 0:
            return "Error: Prompt cannot be empty."
            
        start = time.time()
        payload = {"prompt": prompt}
        if base_image_paths:
            # Convert any relative paths to absolute paths so Gemini server can find the files
            abs_paths = [str(Path(p).resolve()) for p in base_image_paths]
            payload["base_image_paths"] = abs_paths

        _dbg(f"Request -> {self.server_url}")
        _dbg(f"Prompt length: {len(prompt)} characters")
        try:
            response = requests.post(self.server_url, json=payload, timeout=45)
        except requests.Timeout:
            return "Error: Image server timeout after 45s."
        except requests.ConnectionError as ce:
            return f"Error: Cannot connect to image server ({ce}). Ensure server.py running on port 8000." 
        except Exception as e:
            return f"Error: Unexpected exception before response ({e})."

        try:
            response.raise_for_status()
            response_data = response.json()
        except Exception as e:
            return f"Error: Bad response from image server ({e}) status={response.status_code} text={response.text[:200]}"

        if response_data.get("status") == "success" and response_data.get("image_path"):
            source_image_path = response_data["image_path"]
            elapsed = round(time.time() - start, 2)
            _dbg(f"Success in {elapsed}s -> {source_image_path}")
            
            # Handle relative paths from Gemini Image Tutorial
            # The server returns paths like "output\filename.png" 
            # We need to make this an absolute path to the Gemini Image Tutorial directory
            if not os.path.isabs(source_image_path):
                # Gemini Image Tutorial is located at C:\Users\ninic\projects\Datacamp_projects\gemini-image-tutorial
                gemini_tutorial_dir = r"C:\Users\ninic\projects\Datacamp_projects\gemini-image-tutorial"
                source_image_path = os.path.join(gemini_tutorial_dir, source_image_path)
            
            _dbg(f"Resolved source path: {source_image_path}")
            
            # Extract filename from the source path
            source_filename = os.path.basename(source_image_path)
            
            # Define destination directory (comic_panels folder)
            # Use absolute path to avoid working directory issues
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            output_dir = os.path.join(backend_dir, "output", "comic_panels")
            os.makedirs(output_dir, exist_ok=True)
            _dbg(f"Destination directory: {output_dir}")
            
            # Copy the image to our output directory
            destination_path = os.path.join(output_dir, source_filename)
            
            try:
                # Wait a moment for file system to settle (sometimes needed after generation)
                time.sleep(0.5)
                
                # Check if source file exists with retries
                max_retries = 3
                for attempt in range(max_retries):
                    if os.path.exists(source_image_path):
                        break
                    _dbg(f"Source file not found on attempt {attempt + 1}, waiting...")
                    time.sleep(1)
                else:
                    _dbg(f"Source file not found after {max_retries} attempts: {source_image_path}")
                    return f"Image generated but source file not found: {source_image_path}"
                
                # Verify file is readable
                try:
                    with open(source_image_path, 'rb') as f:
                        # Read first few bytes to ensure file is complete
                        f.read(10)
                except Exception as read_error:
                    _dbg(f"Source file not readable: {read_error}")
                    return f"Image generated but source file not readable: {source_image_path}"
                
                # Copy the file from Gemini Image Tutorial to our comic project
                shutil.copy2(source_image_path, destination_path)
                _dbg(f"Image copied to: {destination_path}")
                
                # Verify the copy was successful
                if not os.path.exists(destination_path):
                    _dbg(f"Copy verification failed - destination file not found")
                    return f"Image copy verification failed: {destination_path}"
                
                # Also copy to frontend public directory for web display
                frontend_dir = os.path.join(backend_dir, "..", "frontend", "public", "comic_panels")
                frontend_dir = os.path.normpath(frontend_dir)
                os.makedirs(frontend_dir, exist_ok=True)
                frontend_path = os.path.join(frontend_dir, source_filename)
                
                try:
                    shutil.copy2(destination_path, frontend_path)
                    _dbg(f"Image also copied to frontend: {frontend_path}")
                    
                    # Registry update: Log successful generation and sync
                    from .registry import update_registry_entry
                    
                    # Extract panel number from the prompt (e.g., "Panel 1:", "Panel 2:", etc.)
                    panel_id = None
                    panel_match = re.search(r'panel\s*(\d+)', prompt.lower())
                    if panel_match:
                        panel_number = panel_match.group(1)
                        panel_id = f"panel_{panel_number}"
                        _dbg(f"Extracted panel number from prompt: {panel_id}")
                    else:
                        _dbg("Could not extract panel number from prompt. This is a problem.")
                        # We still need to return the path, but the registry won't be correctly updated
                        # for this specific panel number. The calling agent will need to handle this.

                    if panel_id:
                        update_registry_entry(
                            panel_id=panel_id,
                            filename=source_filename,
                            backend=True,
                            frontend=True,
                            verified=True
                        )
                        _dbg(f"Registry updated for {panel_id} with filename {source_filename}")
                    
                except Exception as frontend_error:
                    _dbg(f"Failed to copy to frontend (non-critical): {frontend_error}")
                
                # Return the filename, which will be used by other tools
                return f"Image generated successfully. Filename: {source_filename}"
                
            except Exception as copy_error:
                _dbg(f"Failed to copy image: {copy_error}")
                return f"Image generated but copy failed: {copy_error}. Original at: {source_image_path}"

        error_message = (
            response_data.get("message")
            or response_data.get("detail")
            or response_data.get("error")
            or "Unknown error from image generation server."
        )
        _dbg(f"Failure: {error_message}")
        return f"Error: {error_message}"

