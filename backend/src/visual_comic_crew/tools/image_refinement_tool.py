import os
from pathlib import Path
from typing import Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
import shutil
import time

class ImageRefinementToolSchema(BaseModel):
    """Input schema for Image Refinement Tool."""
    base_image_path: str = Field(..., description="Path to the base image to refine")
    refinement_prompt: str = Field(..., description="Description of how to refine or modify the image")
    panel_number: int = Field(1, description="Panel number for scene generation")

class ImageRefinementTool(BaseTool):
    """
    Image Refinement Tool using Gemini's image generation with base image refinement.
    Takes an existing comic panel and refines it based on specific requirements.
    Uses the standard Gemini generate-image endpoint with base_image_paths.
    """

    name: str = "Image Refinement Tool"
    description: str = (
        "Refines and modifies existing comic panel images using Gemini's image editing "
        "capabilities. Can apply style transfers, make adjustments, or fine-tune "
        "existing panels based on specific requirements. Use this when you need to "
        "modify an existing image rather than generate a new one from scratch."
    )
    args_schema: Type[BaseModel] = ImageRefinementToolSchema
    server_url: str = os.getenv("GEMINI_IMAGE_SERVER_URL", "http://127.0.0.1:8000/generate-image/")

    def __init__(self):
        super().__init__()

    def _run(
        self,
        base_image_path: str,
        refinement_prompt: str,
        panel_number: int = 1
    ) -> str:
        """
        Refine an existing image using Gemini's image generation with base image reference.

        Args:
            base_image_path: Path to the base image to refine
            refinement_prompt: Description of the refinements to apply
            panel_number: Panel number for naming

        Returns:
            str: Result message with refined image path or error
        """
        try:
            # Validate base image exists
            base_path = Path(base_image_path)
            if not base_path.exists():
                return f"❌ Base image not found: {base_image_path}"

            # Construct refinement prompt that includes the base image context
            full_prompt = f"Panel {panel_number}: Refine and modify the existing comic panel image with these changes: {refinement_prompt}. Maintain the comic art style and character consistency."

            # Prepare request for Gemini generate-image endpoint with base image
            # Convert to absolute path so Gemini server can find the file
            abs_base_path = Path(base_image_path).resolve()
            payload = {
                "prompt": full_prompt,
                "base_image_paths": [str(abs_base_path)]
            }

            print(f"🔄 Refining image for panel {panel_number}: {base_image_path}")

            # Make request to Gemini server using the standard generate-image endpoint
            response = requests.post(
                self.server_url,
                json=payload,
                timeout=120
            )

            if response.status_code != 200:
                return f"❌ Failed to refine image: HTTP {response.status_code} - {response.text}"

            result = response.json()

            if "error" in result:
                return f"❌ Gemini refinement error: {result['error']}"

            if "image_path" not in result:
                return "❌ No image path returned from Gemini refinement operation"

            source_path = Path(result["image_path"])
            if not source_path.exists():
                return f"❌ Refined image not found at {source_path}"

            # Create filename with timestamp for uniqueness
            timestamp = int(time.time() * 1000)
            base_name = base_path.stem  # Get filename without extension
            panel_filename = f"refined_panel_{panel_number:03d}_{base_name}_{timestamp}.png"
            panel_path = Path("output/comic_panels") / panel_filename

            # Ensure comic_panels directory exists
            panel_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the refined image
            shutil.copy2(source_path, panel_path)

            # Also copy to frontend for web display
            frontend_dir = Path("../frontend/public/comic_panels")
            frontend_dir = frontend_dir.resolve()
            frontend_dir.mkdir(parents=True, exist_ok=True)
            frontend_path = frontend_dir / panel_filename

            try:
                shutil.copy2(panel_path, frontend_path)
                print(f"✅ Refined panel also copied to frontend: {frontend_path}")

                # Registry update
                from .registry import update_registry_entry
                panel_id = f"panel_{panel_number}"

                update_registry_entry(
                    panel_id=panel_id,
                    filename=panel_filename,
                    backend=True,
                    frontend=True,
                    verified=True
                )
                print(f"✅ Registry updated: {panel_id} marked as verified")

                return f"✅ Image refined: {panel_filename} (based on {base_path.name})"

            except Exception as frontend_error:
                print(f"⚠️ Failed to copy to frontend (non-critical): {frontend_error}")
                # Still update registry for backend success
                from .registry import update_registry_entry
                update_registry_entry(
                    panel_id=f"panel_{panel_number}",
                    filename=panel_filename,
                    backend=True,
                    frontend=False,
                    verified=False
                )
                print(f"✅ Registry updated: panel_{panel_number} marked as backend-only")

                return f"✅ Image refined (backend only): {panel_filename} (based on {base_path.name})"

        except Exception as e:
            error_msg = f"❌ Error in image refinement: {str(e)}"
            print(error_msg)
            return error_msg