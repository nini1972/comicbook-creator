import os
from pathlib import Path
from typing import List, Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests
import time
from src.utils.image_utils import (
    resolve_image_path,
    retry_file_check,
    verify_image_readable,
    copy_image_to_output,
    update_registry_for_image,
    prepare_temp_images_for_gemini
    )
from src.utils.path_utils import get_backend_output_path, get_frontend_public_path
from src.utils.registry_utils import update_registry_entry


class MultiCharacterSceneToolSchema(BaseModel):
    character_names: List[str] = Field(..., description="List of minimum 2 character names to include in the scene")
    scene_description: str = Field(..., description="Description of the scene/panel with multiple characters")
    panel_number: int = Field(1, description="Panel number for scene generation")

class MultiCharacterSceneTool(BaseTool):
    name: str = "Multi-Character Scene Tool"
    description: str = (
        "Creates comic panels featuring multiple characters in the same scene. "
        "Requires character reference images to exist first (create them with Character Consistency Tool). "
        "Combines 2+ character references into cohesive scenes while maintaining character consistency. "
        "Use when a panel contains multiple named characters interacting together."
    )
    args_schema: Type[BaseModel] = MultiCharacterSceneToolSchema
    server_url: str = os.getenv("GEMINI_IMAGE_SERVER_URL", "http://127.0.0.1:8000/generate-image/")

    def __init__(self):
        super().__init__()

    def _get_character_reference_path(self, character_name: str) -> Optional[Path]:
        # Try several likely locations for character references and be fuzzy on filenames.
        candidates_dirs = []
        
        # src-based and backend-based parents to cover multiple execution contexts
        p = Path(__file__).resolve()
        candidates_dirs = [
        Path.cwd() / "output" / "character_references",
        get_backend_output_path("character_references"),
        get_frontend_public_path("character_references"),
        get_backend_output_path("comic_panels")
        ]
            

        # Normalize and deduplicate directories
        seen = set()
        dirs = []
        for d in candidates_dirs:
            try:
                d_res = d.resolve()
            except Exception:
                d_res = d
            if str(d_res) not in seen:
                seen.add(str(d_res))
                dirs.append(d_res)

        name_tokens = [t for t in character_name.lower().replace('-', ' ').split() if t]

        # Search in candidate directories for obvious exact matches first
        for d in dirs:
            if not d or not d.exists():
                continue
            # check exact patterns
            possible_names = [
                f"{character_name.lower().replace(' ', '_')}_reference.png",
                f"{character_name.lower()}_reference.png",
                f"{character_name.lower().replace(' ', '-')}_reference.png",
            ]
            for filename in possible_names:
                ref_file = d / filename
                if ref_file.exists():
                    return ref_file

        # Fuzzy search: look for any png where filename contains all tokens
        for d in dirs:
            if not d or not d.exists():
                continue
            try:
                for f in d.glob("*.png"):
                    stem = f.stem.lower()
                    if all(tok in stem for tok in name_tokens):
                        return f
            except Exception:
                continue

        return None

    def _run(
        self,
        character_names: List[str],
        scene_description: str,
        panel_number: int = 1
    ) -> str:
        print(f"🎭 DEBUG: MultiCharacterSceneTool called with characters={character_names}, panel={panel_number}")
        try:
            base_paths = []
            missing_characters = []

            for char_name in character_names:
                char_path = self._get_character_reference_path(char_name)
                if char_path:
                    base_paths.append(str(char_path.resolve()))
                else:
                    missing_characters.append(char_name)

            if missing_characters:
                return f"❌ Missing character references for: {', '.join(missing_characters)}. Create character references first."

            if len(base_paths) < 2:
                return "❌ Need at least 2 character images for multi-character scene composition."

            full_prompt = f"Panel {panel_number}: Create a comic scene with multiple characters: {scene_description}. Include all characters consistently in the same scene."

            gemini_paths = prepare_temp_images_for_gemini(base_paths, "temp_multi_character")

            if not gemini_paths:
                print(f"❌ DEBUG: prepare_temp_images_for_gemini returned empty list for base_paths: {base_paths}")
                return f"❌ Failed to prepare character reference images for Gemini access"

            print(f"✅ DEBUG: Prepared {len(gemini_paths)} temp paths for Gemini: {gemini_paths}")

            payload = {
                "prompt": full_prompt,
                "base_image_paths": gemini_paths
            }

            print(f"🔄 Composing multi-character scene for panel {panel_number} with characters: {character_names}")
            print(f"🔄 DEBUG: Sending payload to {self.server_url}")
            print(f"🔄 DEBUG: Payload prompt: {full_prompt}")
            print(f"🔄 DEBUG: Payload base_image_paths: {gemini_paths}")
            response = requests.post(self.server_url, json=payload, timeout=120)

            print(f"🔄 DEBUG: Response status: {response.status_code}")
            print(f"🔄 DEBUG: Response text: {response.text[:500]}")  # First 500 chars

            if response.status_code != 200:
                return f"❌ Failed to compose multi-character scene: HTTP {response.status_code} - {response.text}"

            result = response.json()
            print(f"🔄 DEBUG: Parsed JSON result: {result}")

            if "error" in result:
                return f"❌ Gemini compose error: {result['error']}"

            if "image_path" not in result:
                return "❌ No image path returned from Gemini compose operation"

            source_path = resolve_image_path(result["image_path"])
            if not retry_file_check(source_path):
                return f"❌ Generated image not found after retries: {source_path}"
            if not verify_image_readable(source_path):
                return f"❌ Generated image unreadable: {source_path}"

            timestamp = int(time.time() * 1000)
            char_names_joined = "_".join(char_name.lower().replace(" ", "_") for char_name in character_names[:2])
            panel_filename = f"multi_char_panel_{panel_number:03d}_{char_names_joined}_{timestamp}.png"

            backend_path, frontend_path = copy_image_to_output(source_path, panel_filename)

            panel_id = f"panel_{panel_number}"
            try:
                update_registry_for_image(panel_id, panel_filename, True, True)
                return f"✅ Multi-character scene generated: {panel_filename} (characters: {', '.join(character_names)})"
            except Exception as frontend_error:
                print(f"⚠️ Failed to copy to frontend (non-critical): {frontend_error}")
                update_registry_for_image(panel_id, panel_filename, True, False)
                return f"✅ Multi-character scene generated (backend only): {panel_filename} (characters: {', '.join(character_names)})"

        except Exception as e:
            error_msg = f"❌ Error in multi-character scene generation: {str(e)}"
            print(error_msg)
            return error_msg
