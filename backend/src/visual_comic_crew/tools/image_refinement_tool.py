import os
from pathlib import Path
from typing import Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests
import time
from .image_utils import (
    resolve_image_path,
    retry_file_check,
    verify_image_readable,
    copy_image_to_output,
    update_registry_for_image,
    prepare_temp_images_for_gemini
)

class ImageRefinementToolSchema(BaseModel):
    """Input schema for Image Refinement Tool."""
    base_image_path: str = Field(..., description="Path to the base image to refine")
    refinement_prompt: str = Field(..., description="Description of how to refine or modify the image")
    panel_number: int = Field(1, description="Panel number for scene generation")

class ImageRefinementTool(BaseTool):
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
        print(f"🔧 DEBUG: ImageRefinementTool called with base_image='{base_image_path}', panel={panel_number}")
        try:
            base_path = Path(base_image_path)
            if not base_path.exists():
                return f"❌ Base image not found: {base_image_path}"

            full_prompt = (
                f"Panel {panel_number}: Refine and modify the existing comic panel image with these changes: "
                f"{refinement_prompt}. Maintain the comic art style and character consistency."
            )
            # Prepare base image for Gemini access
            gemini_paths = prepare_temp_images_for_gemini([str(base_path.resolve())], "temp_refinement_images")

            if not gemini_paths:
                    return f"❌ Failed to prepare base image for Gemini access: {base_image_path}"

            payload = {
                "prompt": full_prompt,
                "base_image_paths": gemini_paths
                }

            print(f"🔄 Refining image for panel {panel_number}: {base_image_path}")
            response = requests.post(self.server_url, json=payload, timeout=120)

            if response.status_code != 200:
                return f"❌ Failed to refine image: HTTP {response.status_code} - {response.text}"

            result = response.json()
            if result.get("status") != "success" or "image_path" not in result:
                error_message = (
                    result.get("message")
                    or result.get("detail")
                    or result.get("error")
                    or "Unknown error from image refinement server."
                )
                return f"❌ Refinement failed: {error_message}"

            source_path = resolve_image_path(result["image_path"])
            if not retry_file_check(source_path):
                return f"❌ Refined image not found after retries: {source_path}"

            if not verify_image_readable(source_path):
                return f"❌ Refined image unreadable: {source_path}"

            timestamp = int(time.time() * 1000)
            base_name = base_path.stem
            panel_filename = f"refined_panel_{panel_number:03d}_{base_name}_{timestamp}.png"

            panel_id = f"panel_{panel_number}"
            try:
                backend_path, frontend_path = copy_image_to_output(source_path, panel_filename)
                update_registry_for_image(panel_id, panel_filename, True, True)
                return f"✅ Image refined: {panel_filename} (copied to backend and frontend)"
            except Exception as frontend_error:
                print(f"⚠️ Frontend copy failed: {frontend_error}")
                update_registry_for_image(panel_id, panel_filename, True, False)
                return f"✅ Image refined: {panel_filename} (frontend copy skipped)"

        except Exception as e:
            error_msg = f"❌ Error in image refinement: {str(e)}"
            print(error_msg)
            return error_msg
