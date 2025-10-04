from crewai.tools import BaseTool
import requests
from typing import Type, Optional, List
from pydantic import BaseModel, Field
import os
import time
import shutil
import re
from pathlib import Path
from src.utils.path_utils import get_backend_output_path,get_frontend_public_path
from src.utils.registry_utils import update_registry_entry
from src.utils.image_utils import (
    resolve_image_path,
    retry_file_check,
    verify_image_readable,
    copy_image_to_output,
    extract_panel_id,
    update_registry_for_image
)


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
        "Generates comic panel images from text prompts. Use for panels without specific characters, "
        "background scenes, or when character references don't exist yet. "
        "Does not maintain character consistency - use Character tools for character-specific panels."
    )
    args_schema: Type[BaseModel] = GeminiImageToolSchema
    # Allow override via environment variable GEMINI_IMAGE_SERVER_URL
    server_url: str = os.getenv("GEMINI_IMAGE_SERVER_URL", "http://127.0.0.1:8000/generate-image/")

    def _run(self, prompt: str, base_image_paths: Optional[List[str]] = None) -> str:
        """Generate an image and return the saved path or an error string."""
        # Defensive handling: tool callers may sometimes pass a stringified JSON blob
        # (e.g. '"{\"prompt\": ...}"') — try to normalize it into structured args.
        try:
            debug_prompt_preview = prompt[:50] if isinstance(prompt, str) else str(prompt)[:50]
        except Exception:
            debug_prompt_preview = "<unpreviewable>"

        print(f"🎨 DEBUG: GeminiImageTool called with prompt='{debug_prompt_preview}...', base_images={len(base_image_paths) if base_image_paths else 0}")

        # If prompt looks like a JSON string containing the actual payload, try to parse it.
        if isinstance(prompt, str):
            stripped = prompt.strip()
            if (stripped.startswith('{') and stripped.endswith('}')) or (
                stripped.startswith('"{') and stripped.endswith('}"')
            ):
                import json as _json
                try:
                    # If it's double-quoted JSON like '"{...}"', unquote first
                    if stripped.startswith('"') and stripped.endswith('"'):
                        stripped = stripped[1:-1]
                    parsed = _json.loads(stripped)
                    if isinstance(parsed, dict):
                        # Pull out expected keys if present
                        if 'prompt' in parsed:
                            prompt = parsed.get('prompt')
                        if 'base_image_paths' in parsed:
                            base_image_paths = parsed.get('base_image_paths')
                except Exception:
                    # If parsing fails, continue with original prompt value
                    pass

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
            source_path = resolve_image_path(source_image_path)
         
            _dbg(f"Resolved source path: {source_path}")
            
            # Extract panel number from the prompt (e.g., "Panel 1:", "Panel 2:", etc.)
            panel_id = extract_panel_id(prompt)
            
            # Extract filename from the source path
            source_filename = os.path.basename(source_image_path)
            
            # If panel number is mentioned in prompt, modify filename to include it
            if panel_id:
                # Extract panel number from panel_id (e.g., "panel_1" -> "001")
                panel_number = panel_id.split('_')[1]
                # Create new filename with panel number
                name_part, ext = os.path.splitext(source_filename)
                panel_filename = f"panel_{panel_number:0>3}_{name_part}{ext}"
            else:
                panel_filename = source_filename
            # Define destination directory (comic_panels folder)
            # Use absolute path to avoid working directory issues
            output_dir = get_backend_output_path("comic_panels")
            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True)
            _dbg(f"Destination directory: {output_dir}")
            
            # Copy the image to our output directory
            destination_path = os.path.join(output_dir, panel_filename)
            
            try:
                # Wait a moment for file system to settle (sometimes needed after generation)
                time.sleep(0.5)
                
                # Check if source file exists with retries
                if not retry_file_check(source_path):
                    return f"Image generated but source file not found: {source_path}"
                               
                # Verify file is readable
                if not verify_image_readable(source_path):
                    return f"Image generated but source file not readable: {source_path}"

                # Copy the file from Gemini Image Tutorial to our comic project
                backend_path, frontend_path = copy_image_to_output(source_path, panel_filename)

                _dbg(f"Copied to backend: {backend_path}")
                _dbg(f"Copied to frontend: {frontend_path}") 

                if panel_id:
                    update_registry_for_image(panel_id, panel_filename, True, True)

                    _dbg(f"Registry updated for {panel_id} with filename {panel_filename}")
                   # Return the filename, which will be used by other tools
                    return f"Image generated successfully. Filename: {panel_filename}"
                else:
                    _dbg("Warning: Could not extract panel ID from prompt, registry not updated.")
                     # Return the filename, which will be used by other tools
                    return f"Image registered unsuccessfully, panel_id is missing. Filename: {panel_filename}"
                
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

