import os
from pathlib import Path
from typing import Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests
import time
from src.utils.registry_utils import update_registry_entry
from src.image_generator.core import generate_image
from src.image_generator.core import generate_image
from src.utils.image_utils import (
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

            pil_images = []
            for path_str in gemini_paths:
                path = Path(path_str).resolve()
                if not path.exists():
                    return f"❌ Error: Base image not found: {path_str}"
                try:
                    from PIL import Image
                    pil_images.append(Image.open(path))
                except Exception as e:
                    return f"❌ Error: Failed to open base image {path_str}: {e}"

            print(f"🔄 Refining image for panel {panel_number}: {base_image_path}")
            
            generated_image = generate_image(full_prompt, pil_images)

            if not generated_image:
                return "❌ Error: Image refinement failed. The model may have returned an empty response due to safety filters."

            timestamp = int(time.time() * 1000)
            base_name = base_path.stem
            panel_filename = f"refined_panel_{panel_number:03d}_{base_name}_{timestamp}.png"

            from src.utils.path_utils import get_backend_output_path, get_frontend_public_path
            
            # Define destination directory (comic_panels folder)
            output_dir = get_backend_output_path("comic_panels")
            os.makedirs(output_dir, exist_ok=True)
            
            # Save the image directly to our output directory
            destination_path = os.path.join(output_dir, panel_filename)
            generated_image.save(destination_path)
            
            print(f"✅ Saved to backend: {destination_path}")
            
            # Also copy to frontend
            import shutil
            frontend_dir = get_frontend_public_path("comic_panels")
            os.makedirs(frontend_dir, exist_ok=True)
            frontend_path = os.path.join(frontend_dir, panel_filename)
            shutil.copy2(destination_path, frontend_path)
            print(f"✅ Copied to frontend: {frontend_path}")

            panel_id = f"panel_{panel_number}"
            try:
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
