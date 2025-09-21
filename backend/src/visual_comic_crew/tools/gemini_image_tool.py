from crewai.tools import BaseTool
import requests
from typing import Type, Optional, List
from pydantic import BaseModel, Field
import os
import time
import shutil
import re

# Simple helper for debug prints (could be replaced with logging module later)
def _dbg(msg: str):
    print(f"[GeminiImageTool] {msg}")

class GeminiImageToolSchema(BaseModel):
    """Input for GeminiImageTool."""
    prompt: str = Field(..., description="The detailed prompt for image generation.")
    base_image_paths: Optional[List[str]] = Field(None, description="Optional list of local file paths for base images to be used as reference.")

class GeminiImageTool(BaseTool):
    name: str = "Gemini Image Generator"
    description: str = (
        "Generates a comic panel image using the local image server (Gemini Flash). "
        "Provide a detailed prompt including characters, style, perspective, and mood."
    )
    args_schema: Type[BaseModel] = GeminiImageToolSchema
    # Allow override via environment variable GEMINI_IMAGE_SERVER_URL
    server_url: str = os.getenv("GEMINI_IMAGE_SERVER_URL", "http://127.0.0.1:8000/generate-image/")

    def _run(self, prompt: str, base_image_paths: Optional[List[str]] = None) -> str:
        """Generate an image and return the saved path or an error string."""
        start = time.time()
        payload = {"prompt": prompt}
        if base_image_paths:
            payload["base_image_paths"] = base_image_paths

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
            output_dir = os.path.join(os.getcwd(), "output", "comic_panels")
            os.makedirs(output_dir, exist_ok=True)
            
            # Copy the image to our output directory
            destination_path = os.path.join(output_dir, source_filename)
            
            try:
                # Check if source file exists
                if not os.path.exists(source_image_path):
                    _dbg(f"Source file not found: {source_image_path}")
                    return f"Image generated but source file not found: {source_image_path}"
                
                # Copy the file from Gemini Image Tutorial to our comic project
                shutil.copy2(source_image_path, destination_path)
                _dbg(f"Image copied to: {destination_path}")
                
                # Return the relative path that can be used in markdown
                relative_path = f"output/comic_panels/{source_filename}"
                return f"Image generated successfully. Local path: {relative_path}"
                
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

