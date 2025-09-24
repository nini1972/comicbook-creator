import os
from pathlib import Path
from typing import List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
import shutil
import time

class MultiCharacterSceneToolSchema(BaseModel):
    """Input schema for Multi-Character Scene Tool."""
    character_names: List[str] = Field(..., description="List of character names to include in the scene")
    scene_description: str = Field(..., description="Description of the scene/panel with multiple characters")
    panel_number: int = Field(1, description="Panel number for scene generation")

class MultiCharacterSceneTool(BaseTool):
    """
    Multi-Character Scene Tool using Gemini's image generation with multiple base images.
    Combines multiple character reference images into a single scene.
    Uses the standard Gemini generate-image endpoint with multiple base_image_paths.
    """

    name: str = "Multi-Character Scene Tool"
    description: str = (
        "Creates comic panels with multiple characters by composing multiple character "
        "reference images into a single scene. Uses Gemini's compose_images function "
        "to maintain character consistency across multiple characters in the same panel. "
        "Use this when a scene requires two or more named characters to appear together."
    )
    args_schema: Type[BaseModel] = MultiCharacterSceneToolSchema
    server_url: str = os.getenv("GEMINI_IMAGE_SERVER_URL", "http://127.0.0.1:8000/generate-image/")

    def __init__(self):
        super().__init__()

    def _get_character_reference_path(self, character_name: str) -> Optional[Path]:
        """Get the path to a character's reference image."""
        char_ref_dir = Path("output/character_references")
        if not char_ref_dir.exists():
            return None

        # Look for character reference files
        for ref_file in char_ref_dir.glob(f"{character_name.lower().replace(' ', '_')}_reference.png"):
            return ref_file

        # Also try exact filename match
        exact_path = char_ref_dir / f"{character_name.lower().replace(' ', '_')}_reference.png"
        if exact_path.exists():
            return exact_path

        return None

    def _run(
        self,
        character_names: List[str],
        scene_description: str,
        panel_number: int = 1
    ) -> str:
        """
        Generate a scene with multiple characters using Gemini's compose_images.

        Args:
            character_names: List of character names to include
            scene_description: Description of the scene
            panel_number: Panel number for naming

        Returns:
            str: Result message with generated image path or error
        """
        try:
            # Validate character references exist
            character_paths = []
            missing_characters = []

            for char_name in character_names:
                char_path = self._get_character_reference_path(char_name)
                if char_path:
                    # Convert to absolute path so Gemini server can find the file
                    abs_path = char_path.resolve()
                    character_paths.append(str(abs_path))
                else:
                    missing_characters.append(char_name)

            if missing_characters:
                return f"❌ Missing character references for: {', '.join(missing_characters)}. Create character references first."

            if len(character_paths) < 2:
                return "❌ Need at least 2 character images for multi-character scene composition."

            # Prepare request for Gemini generate-image with multiple base images
            full_prompt = f"Panel {panel_number}: Create a comic scene with multiple characters: {scene_description}. Include all characters consistently in the same scene."

            payload = {
                "prompt": full_prompt,
                "base_image_paths": character_paths
            }

            print(f"🔄 Composing multi-character scene for panel {panel_number} with characters: {character_names}")

            # Make request to Gemini server using the standard generate-image endpoint
            response = requests.post(
                self.server_url,
                json=payload,
                timeout=120
            )

            if response.status_code != 200:
                return f"❌ Failed to compose multi-character scene: HTTP {response.status_code} - {response.text}"

            result = response.json()

            if "error" in result:
                return f"❌ Gemini compose error: {result['error']}"

            if "image_path" not in result:
                return "❌ No image path returned from Gemini compose operation"

            source_path = Path(result["image_path"])
            if not source_path.exists():
                return f"❌ Generated image not found at {source_path}"

            # Create filename with timestamp for uniqueness
            timestamp = int(time.time() * 1000)
            char_names_joined = "_".join(char_name.lower().replace(" ", "_") for char_name in character_names[:2])  # Limit to first 2 for filename
            panel_filename = f"multi_char_panel_{panel_number:03d}_{char_names_joined}_{timestamp}.png"
            panel_path = Path("output/comic_panels") / panel_filename

            # Ensure comic_panels directory exists
            panel_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the generated image
            shutil.copy2(source_path, panel_path)

            # Also copy to frontend for web display
            frontend_dir = Path("../frontend/public/comic_panels")
            frontend_dir = frontend_dir.resolve()
            frontend_dir.mkdir(parents=True, exist_ok=True)
            frontend_path = frontend_dir / panel_filename

            try:
                shutil.copy2(panel_path, frontend_path)
                print(f"✅ Multi-character panel also copied to frontend: {frontend_path}")

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

                return f"✅ Multi-character scene generated: {panel_filename} (characters: {', '.join(character_names)})"

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

                return f"✅ Multi-character scene generated (backend only): {panel_filename} (characters: {', '.join(character_names)})"

        except Exception as e:
            error_msg = f"❌ Error in multi-character scene generation: {str(e)}"
            print(error_msg)
            return error_msg