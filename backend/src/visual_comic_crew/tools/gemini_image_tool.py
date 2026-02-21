from crewai.tools import BaseTool
from typing import Type, Optional, List
from pydantic import BaseModel, Field
import os
import time
import shutil
import re
from pathlib import Path
from PIL import Image
from src.utils.path_utils import get_backend_output_path,get_frontend_public_path
from src.utils.registry_utils import update_registry_entry
from src.utils.image_utils import (
    extract_panel_id,
    update_registry_for_image,
    copy_image_to_output
)
from src.image_generator.core import generate_image

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
        
        pil_images = []
        if base_image_paths:
            for path_str in base_image_paths:
                path = Path(path_str).resolve()
                if not path.exists():
                    return f"Error: Base image not found: {path_str}"
                try:
                    pil_images.append(Image.open(path))
                except Exception as e:
                    return f"Error: Failed to open base image {path_str}: {e}"

        _dbg(f"Prompt length: {len(prompt)} characters")
        try:
            generated_image = generate_image(
                prompt=prompt,
                base_images=pil_images if pil_images else None
            )
            
            if not generated_image:
                return "Error: Image generation failed. The model may have returned an empty response due to safety filters."
                
            elapsed = round(time.time() - start, 2)
            _dbg(f"Success in {elapsed}s")
            
            # Extract panel number from the prompt (e.g., "Panel 1:", "Panel 2:", etc.)
            panel_id = extract_panel_id(prompt)
            
            # Use timestamp-based naming to guarantee uniqueness
            timestamp = int(time.time() * 1000)
            
            # If panel number is mentioned in prompt, modify filename to include it
            if panel_id:
                # Extract panel number from panel_id (e.g., "panel_1" -> "001")
                panel_number = panel_id.split('_')[1]
                panel_filename = f"panel_{panel_number:0>3}_{timestamp}.png"
            else:
                panel_filename = f"generated_{timestamp}.png"
                
            # Define destination directory (comic_panels folder)
            output_dir = get_backend_output_path("comic_panels")
            os.makedirs(output_dir, exist_ok=True)
            
            # Save the image directly to our output directory with explicit error handling
            destination_path = os.path.join(output_dir, panel_filename)
            try:
                generated_image.save(destination_path)
                if os.path.exists(destination_path):
                    file_size = os.path.getsize(destination_path)
                    _dbg(f"Saved to backend: {destination_path} ({file_size} bytes)")
                else:
                    _dbg(f"ERROR: Save appeared to succeed but file not found: {destination_path}")
            except Exception as save_error:
                _dbg(f"ERROR saving to backend: {save_error}")
                raise  # Re-raise to prevent silent failure
            
            # Also copy to frontend
            frontend_dir = get_frontend_public_path("comic_panels")
            os.makedirs(frontend_dir, exist_ok=True)
            frontend_path = os.path.join(frontend_dir, panel_filename)
            try:
                if not os.path.exists(destination_path):
                    raise FileNotFoundError(f"Backend file missing before copy: {destination_path}")
                shutil.copy2(destination_path, frontend_path)
                if os.path.exists(frontend_path):
                    _dbg(f"Copied to frontend: {frontend_path}")
                else:
                    _dbg(f"ERROR: Copy appeared to succeed but frontend file not found: {frontend_path}")
            except Exception as copy_error:
                _dbg(f"ERROR copying to frontend: {copy_error}")
                # Don't raise - frontend copy is non-critical

            if panel_id:
                update_registry_for_image(panel_id, panel_filename, True, True)
                _dbg(f"Registry updated for {panel_id} with filename {panel_filename}")
                return f"Image generated successfully. Filename: {panel_filename}"
            else:
                _dbg("Warning: Could not extract panel ID from prompt, registry not updated.")
                return f"Image registered unsuccessfully, panel_id is missing. Filename: {panel_filename}"
                
        except Exception as e:
            _dbg(f"Failure: {e}")
            return f"Error: Unexpected exception during generation ({e})."

