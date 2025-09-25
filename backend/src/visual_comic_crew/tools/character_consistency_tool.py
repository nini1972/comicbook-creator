import os
from pathlib import Path
from PIL import Image
from typing import Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
import shutil
import time
import hashlib

from .image_utils import (
    resolve_image_path,
    retry_file_check,
    verify_image_readable,
    copy_image_to_output,
    update_registry_for_image,
    prepare_temp_images_for_gemini
)

class CharacterConsistencyToolSchema(BaseModel):
    """Input schema for Character Consistency Tool."""
    action: str = Field(..., description="Action to perform: 'create_character', 'generate_scene', or 'list_characters'")
    character_name: Optional[str] = Field(None, description="Name of the character (required for create_character and generate_scene)")
    character_description: Optional[str] = Field(None, description="Detailed description of character appearance (required for create_character)")
    scene_description: Optional[str] = Field(None, description="Description of the scene/panel (required for generate_scene)")
    panel_number: Optional[int] = Field(1, description="Panel number for scene generation")
    existing_image_path: Optional[str] = Field(None, description="Path to existing character image for enhancement (optional)")

class CharacterConsistencyTool(BaseTool):
    """
    Enhanced Character Consistency Tool based on Gemini Image Tutorial Option 6.
    Creates character reference sheets and generates consistent character images
    across multiple comic panels, maintaining the same character appearance.
    
    OPTIMIZATIONS:
    - Panel generation caching to prevent duplicate calls
    - Efficient dual image handling from Gemini server
    - Better error handling to prevent retry loops
    """
    
    name: str = "Character Consistency Tool"
    description: str = (
        "Manages character creation and consistent character appearance across comic panels. "
        "Use 'create_character' action to create new character reference sheets. "
        "Use 'generate_scene' action to generate comic panels with existing characters, "
        "maintaining consistent appearance. Use 'list_characters' to see available characters. "
        "Essential for maintaining character consistency throughout comic stories."
    )
    args_schema: Type[BaseModel] = CharacterConsistencyToolSchema
    server_url: str = os.getenv("GEMINI_IMAGE_SERVER_URL", "http://127.0.0.1:8000/generate-image/")

    def __init__(self):
        super().__init__()
        
    def _get_character_cache_path(self) -> Path:
        """Get the path to the character cache file"""
        cache_dir = Path("output/character_references")
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / "character_cache.txt"
    
    def _get_panel_cache_path(self) -> Path:
        """Get the path to the panel generation cache file"""
        cache_dir = Path("output/character_references")
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / "panel_cache.txt"
    
    def _generate_panel_cache_key(self, character_name: str, scene_description: str, panel_number: int) -> str:
        """Generate a unique cache key for panel generation"""
        content = f"{character_name.lower()}_{panel_number}_{scene_description}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_panel_cache(self, character_name: str, scene_description: str, panel_number: int) -> Optional[str]:
        """Check if this panel has already been generated recently"""
        cache_file = self._get_panel_cache_path()
        if not cache_file.exists():
            return None
            
        cache_key = self._generate_panel_cache_key(character_name, scene_description, panel_number)
        
        try:
            with open(cache_file, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, path = line.strip().split('=', 1)
                        if key == cache_key and Path(path).exists():
                            print(f"🎯 Found cached panel for {character_name} panel {panel_number}: {path}")
                            return path
        except Exception:
            pass
        
        return None
    
    def _save_panel_cache(self, character_name: str, scene_description: str, panel_number: int, panel_path: str):
        """Save panel generation to cache"""
        cache_file = self._get_panel_cache_path()
        cache_key = self._generate_panel_cache_key(character_name, scene_description, panel_number)
        
        try:
            # Read existing cache
            cache_data = {}
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            cache_data[key] = value
            
            # Add new panel
            cache_data[cache_key] = panel_path
            
            # Keep only recent entries (last 10 panels to avoid cache bloat)
            if len(cache_data) > 10:
                # Keep only the last 10 entries
                cache_items = list(cache_data.items())[-10:]
                cache_data = dict(cache_items)
            
            # Write back to file
            with open(cache_file, 'w') as f:
                for key, value in cache_data.items():
                    f.write(f"{key}={value}\n")
                    
            print(f"💾 Panel cached: {character_name} panel {panel_number}")
        except Exception as e:
            print(f"Warning: Could not save panel cache: {e}")
    
    def _save_character_reference(self, character_name: str, reference_path: str):
        """Save character reference path to cache file"""
        cache_file = self._get_character_cache_path()
        try:
            # Read existing cache
            cache_data = {}
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            cache_data[key] = value
            
            # Add new reference
            cache_data[character_name.lower()] = reference_path
            
            # Write back to file
            with open(cache_file, 'w') as f:
                for key, value in cache_data.items():
                    f.write(f"{key}={value}\n")
                    
            print(f"📚 Character reference cached: {character_name} -> {reference_path}")
        except Exception as e:
            print(f"Warning: Could not save character cache: {e}")
    
    def _get_character_reference(self, character_name: str) -> Optional[str]:
        """Get character reference path from cache or file system"""
        cache_file = self._get_character_cache_path()
        character_key = character_name.lower()
        
        print(f"🔍 DEBUG: Looking for character reference for '{character_name}' (key: '{character_key}')")
        
        # First try the cache file
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key == character_key:
                                if Path(value).exists():
                                    print(f"✅ DEBUG: Found cached reference: {value}")
                                    return value
                                else:
                                    print(f"⚠️ DEBUG: Cached reference {value} not found, removing from cache")
            except Exception as e:
                print(f"⚠️ DEBUG: Error reading cache: {e}")
        
        # Fallback: look for existing reference file
        reference_path = Path(f"output/character_references/{character_key}_reference.png")
        print(f"🔍 DEBUG: Checking filesystem for: {reference_path}")
        if reference_path.exists():
            # Save to cache for next time
            self._save_character_reference(character_name, str(reference_path))
            print(f"✅ DEBUG: Found reference on filesystem: {reference_path}")
            return str(reference_path)
        
        print(f"❌ DEBUG: No reference found for '{character_name}'")
        return None

    def _generate_image_via_server(self, prompt: str, base_image_paths: Optional[list] = None, single_call: bool = False) -> str:
        """
        Generate image using the existing Gemini server infrastructure.
        Enhanced with Option 6 approach for character consistency.
        
        Args:
            prompt: The image generation prompt
            base_image_paths: Optional character reference paths
            single_call: If True, only make one call to avoid duplicate generation
        """
        try:
            payload = {"prompt": prompt}
            if base_image_paths:
                payload["base_image_paths"] = base_image_paths
                print(f"🎭 Using character reference(s): {base_image_paths}")

            print(f"🎨 Generating image with prompt: {prompt[:100]}...")
            
            # Make only one call if single_call is True to prevent duplicates
            if single_call:
                print(f"⚡ Single-call mode: optimized generation")
            
            response = requests.post(self.server_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                # Handle both response formats for compatibility
                if result.get("status") == "success" or result.get("success"):
                    generated_path = result.get("image_path", result.get("local_path", ""))
                    print(f"✅ Image generated successfully: {generated_path}")
                    return generated_path
                else:
                    error_msg = result.get('error', result.get('message', 'Unknown error'))
                    print(f"❌ Server error: {error_msg}")
                    return f"❌ Server error: {error_msg}"
            else:
                error_msg = f"HTTP error {response.status_code}: {response.text}"
                print(f"❌ {error_msg}")
                return f"❌ {error_msg}"
                
        except Exception as e:
            error_msg = f"Error during image generation: {str(e)}"
            print(f"❌ {error_msg}")
            return f"❌ {error_msg}"

    def create_character_reference(self, character_name: str, character_description: str, existing_image_path: str = None) -> str:
        """
        Creates a character reference image (Option 6 approach).
        Can create from scratch or enhance an existing image.
        
        Args:
            character_name (str): Name of the character (e.g., "Lyra", "Nimbus")
            character_description (str): Detailed description of the character
            existing_image_path (str, optional): Path to existing character image to enhance
            
        Returns:
            str: Path to the saved character reference image or error message
        """
        print(f"👤 DEBUG: create_character_reference called for '{character_name}'")
        try:
            print(f"👤 Creating character reference for {character_name}...")
            
            if existing_image_path and Path(existing_image_path).exists():
                # Option 6 approach: enhance existing character image
                reference_prompt = f"{character_description} standing in neutral pose"
                result = self._generate_image_via_server(reference_prompt, [existing_image_path])
            else:
                # Option 6 approach: create character from scratch
                reference_prompt = f"{character_description} standing in neutral pose"
                result = self._generate_image_via_server(reference_prompt)
            
            if result.startswith("❌"):
                return result
            
            # Handle relative paths from Gemini Image Tutorial (same as GeminiImageTool)
            source_image_path = result
            source_path = resolve_image_path(source_image_path)

            
            # Check if source file exists
            if not source_path.exists():
                return f"❌ Generated character reference not found at {source_image_path}"
            
            # for readibility Check if image is readable
            if not retry_file_check(source_path):
                return f"❌ Character reference not found after retries: {source_path}"
            
            if not verify_image_readable(source_path):
                return f"❌ Character reference unreadable: {source_path}"

            # Create character references directory
            char_ref_dir = Path("output/character_references")
            char_ref_dir.mkdir(parents=True, exist_ok=True)
            
            # Create new filename for character reference
            reference_path = char_ref_dir / f"{character_name.lower()}_reference.png"
            
            # Copy the generated image to character references
            # Use direct copy instead of copy_image_to_output since character refs go to different folder
            shutil.copy2(source_path, reference_path)
            
            # Also copy to frontend character references for consistency
            frontend_char_ref_dir = Path("../frontend/public/character_references")
            frontend_char_ref_dir.mkdir(parents=True, exist_ok=True)
            frontend_ref_path = frontend_char_ref_dir / reference_path.name
            shutil.copy2(source_path, frontend_ref_path)
            
            backend_path = reference_path
            frontend_path = frontend_ref_path

            # Store the path for future use
            self._save_character_reference(character_name, str(backend_path))

            
            print(f"✅ Character reference for {character_name} saved to {reference_path}")
            return str(reference_path)
            
        except Exception as e:
            error_msg = f"Error creating character reference for {character_name}: {str(e)}"
            print(f"❌ {error_msg}")
            return f"❌ {error_msg}"

    def generate_character_scene(self, character_name: str, scene_description: str, panel_number: int = 1) -> str:
        """
        Generates a comic panel with the specified character in a new scene (Option 6 approach).
        Uses character reference to maintain consistency.
        
        OPTIMIZATIONS:
        - Checks cache first to avoid duplicate generation
        - Uses single-call mode to prevent dual image generation
        - Better error handling and cleanup
        
        Args:
            character_name (str): Name of the character to include
            scene_description (str): Description of the scene/panel
            panel_number (int): Panel number for filename
            
        Returns:
            str: Path to the generated panel image or error message
        """
        print(f"🎬 DEBUG: generate_character_scene called for '{character_name}' in panel {panel_number}")
        try:
            character_key = character_name.lower()
            
            # OPTIMIZATION: Check panel cache first
            cached_panel = self._check_panel_cache(character_name, scene_description, panel_number)
            if cached_panel:
                print(f"🎯 DEBUG: Using cached panel: {cached_panel}")
                return cached_panel
            
            # Check if we have a character reference (Option 6 requirement)
            reference_path = self._get_character_reference(character_name)
            if not reference_path:
                error_msg = (f"❌ No character reference found for {character_name}. "
                           f"Please create a character reference first using 'create_character' action.")
                print(f"❌ DEBUG: {error_msg}")
                return error_msg
            
            print(f"📚 Using character reference for {character_name}: {reference_path}")
            
            # Convert to absolute path first to ensure it exists
            if not os.path.isabs(reference_path):
                reference_path = os.path.abspath(reference_path)
            
            # Verify the reference file exists
            if not Path(reference_path).exists():
                return f"❌ Character reference file not found at {reference_path}"
            
            gemini_paths = prepare_temp_images_for_gemini([str(Path(reference_path).resolve())], "temp_character_refs")
            if not gemini_paths:
                return f"❌ Failed to prepare character reference for Gemini access: {reference_path}"

            server_absolute_path = gemini_paths[0]

            
            # Option 6 approach: place character from reference into new scene
            scene_prompt = f"Panel {panel_number}: {scene_description}"
            
            print(f"🎬 Generating panel {panel_number} with {character_name}...")
            print(f"🎭 Using absolute reference for Gemini server: {server_absolute_path}")
            
            # OPTIMIZATION: Use single-call mode to prevent duplicate generation
            result = self._generate_image_via_server(scene_prompt, [server_absolute_path], single_call=True)
            
            if result.startswith("❌"):
                try:
                    temp_path = Path(server_absolute_path)
                    if temp_path.exists():
                        temp_path.unlink()
                        print(f"🧹 Temp file deleted: {temp_path}")
                except Exception as cleanup_error:
                    print(f"⚠️ Failed to delete temp file: {cleanup_error}")

                return result
            
            # Handle relative paths from Gemini Image Tutorial (same as character reference creation)
            source_image_path = result
            source_path = resolve_image_path(source_image_path)
            
            # Move to consistent panels in comic_panels directory
            if not retry_file_check(source_path):
                try:
                    temp_path = Path(server_absolute_path)
                    if temp_path.exists():
                        temp_path.unlink()
                        print(f"🧹 Temp file deleted: {temp_path}")
                except Exception as cleanup_error:
                    print(f"⚠️ Failed to delete temp file: {cleanup_error}")

                return f"❌ Generated panel not found after retries: {source_path}"

            if not verify_image_readable(source_path):
                try:
                    temp_path = Path(server_absolute_path)
                    if temp_path.exists():
                        temp_path.unlink()
                        print(f"🧹 Temp file deleted: {temp_path}")
                except Exception as cleanup_error:
                    print(f"⚠️ Failed to delete temp file: {cleanup_error}")

                return f"❌ Generated panel unreadable: {source_path}"

            
            
            # Create filename for consistent panel
            panel_filename = f"consistent_panel_{panel_number:03d}_{character_key}_{int(time.time() * 1000)}.png"
            panel_path = Path("output/comic_panels") / panel_filename
            
            # Define panel_id for registry updates
            panel_id = f"panel_{panel_number}"

            # Ensure comic_panels directory exists
            panel_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the generated image
            try:
                backend_path, frontend_path = copy_image_to_output(source_path, panel_filename)

                print(f"✅ Character panel also copied to frontend: {frontend_path}")
                
                update_registry_for_image(panel_id, panel_filename, True, True)

                print(f"✅ Registry updated: {panel_id} marked as verified")
                
            except Exception as frontend_error:
                print(f"⚠️ Failed to copy to frontend (non-critical): {frontend_error}")
                # Still update registry for backend success
                update_registry_for_image(panel_id, panel_filename, True, False)

                print(f"✅ Registry updated: {panel_id} marked as backend-only")
            
            # OPTIMIZATION: Save to panel cache for future use
            self._save_panel_cache(character_name, scene_description, panel_number, str(panel_path))
            
            print(f"✅ Panel {panel_number} with {character_name} saved to {panel_path}")
            return str(panel_path)
        
        except Exception as e:
            error_msg = f"Error generating scene with {character_name}: {str(e)}"
            print(f"❌ {error_msg}")
            return f"❌ {error_msg}"
        
        finally:
            # Always Clean up temporary reference file
            try:
                if 'server_absolute_path' in locals():
                    temp_path = Path(server_absolute_path)
                    if temp_path.exists():
                        temp_path.unlink()
                        print(f"🧹 Cleaned up temporary reference file: {temp_path}")
            except Exception as cleanup_error:
                print(f"⚠️ Failed to clean up temporary reference file: {cleanup_error}")

            
        
            


    def list_character_references(self) -> str:
        """List all available character references"""
        try:
            char_ref_dir = Path("output/character_references")
            if not char_ref_dir.exists():
                return "📚 No character references directory found."
            
            references = list(char_ref_dir.glob("*_reference.png"))
            if not references:
                return "📚 No character references found."
            
            result = "📚 Available character references:\n"
            for ref in references:
                character_name = ref.stem.replace("_reference", "").title()
                result += f"   - {character_name}: {ref}\n"
            
            return result.strip()
            
        except Exception as e:
            return f"❌ Error listing character references: {str(e)}"

    def _run(
        self, 
        action: str,
        character_name: Optional[str] = None,
        character_description: Optional[str] = None,
        scene_description: Optional[str] = None,
        panel_number: int = 1,
        existing_image_path: Optional[str] = None
    ) -> str:
        """
        Main execution method for the enhanced Character Consistency Tool.
        Now uses proper schema-based parameter handling.
        
        Args:
            action (str): "create_character", "generate_scene", or "list_characters"
            character_name (str, optional): Name of the character
            character_description (str, optional): Detailed description for character creation
            scene_description (str, optional): Scene description for panel generation
            panel_number (int): Panel number (default: 1)
            existing_image_path (str, optional): Path to existing character image
            
        Returns:
            str: Result message with file path or error
        """
        # Normalize action string
        action = action.lower().strip()
        print(f"🔧 DEBUG: CharacterConsistencyTool._run called with action='{action}', character_name='{character_name}'")
        
        if action in ["create_character", "create", "character"]:
            if not character_name or not character_description:
                return "❌ Both character_name and character_description are required for create_character action"
            
            return self.create_character_reference(character_name, character_description, existing_image_path)
            
        elif action in ["generate_scene", "generate", "scene"]:
            if not character_name or not scene_description:
                return "❌ Both character_name and scene_description are required for generate_scene action"
            
            return self.generate_character_scene(character_name, scene_description, panel_number)
            
        elif action in ["list_characters", "list"]:
            return self.list_character_references()
            
        else:
            return f"❌ Unknown action: {action}. Use 'create_character', 'generate_scene', or 'list_characters'"