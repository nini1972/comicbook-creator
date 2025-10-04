import os
import time
import shutil
import re
from pathlib import Path
from typing import Optional, Tuple,List
from src.utils.registry_utils import update_registry_entry
from src.utils.path_utils import get_backend_output_path, get_frontend_public_path

# Base directory for Gemini image server
GEMINI_BASE_DIR = os.getenv("GEMINI_IMAGE_ROOT", r"C:\Users\ninic\projects\Datacamp_projects\gemini-image-tutorial")

def prepare_temp_images_for_gemini(base_image_paths: List[str], temp_folder_name: str) -> List[str]:
    """
    Copies base images to a Gemini-accessible temp folder and returns their absolute paths.

    Args:
        base_image_paths (List[str]): List of image paths from ComicBook side
        temp_folder_name (str): Name of the temp folder inside Gemini-Image-Tutorial

    Returns:
        List[str]: List of absolute paths inside Gemini temp folder
    """
    gemini_root = Path(os.getenv("GEMINI_IMAGE_ROOT", "C:/Users/ninic/projects/Datacamp_projects/gemini-image-tutorial"))
    temp_dir = gemini_root / temp_folder_name
    temp_dir.mkdir(parents=True, exist_ok=True)

    copied_paths = []
    for path_str in base_image_paths:
        src_path = Path(path_str).resolve()
        if not src_path.exists():
            print(f"⚠️ Source image not found: {src_path}")
            continue

        # Create unique filename to avoid collisions
        filename = src_path.name
        dest_path = temp_dir / filename

        try:
            shutil.copy2(src_path, dest_path)
            copied_paths.append(str(dest_path.resolve()))
            print(f"📁 Copied to Gemini temp folder: {dest_path}")
        except Exception as e:
            print(f"⚠️ Failed to copy {src_path} to Gemini temp folder: {e}")

    return copied_paths

def resolve_image_path(relative_path: str) -> Path:
    """Convert relative image path from Gemini server to absolute path."""
    path = Path(relative_path)
    if not path.is_absolute():
        return Path(GEMINI_BASE_DIR) / path
    return path

def retry_file_check(path: Path, retries: int = 3, delay: float = 1.0) -> bool:
    """Wait and retry until file exists."""
    for _ in range(retries):
        if path.exists():
            return True
        time.sleep(delay)
    return False

def verify_image_readable(path: Path) -> bool:
    """Check if image file is readable."""
    try:
        with open(path, 'rb') as f:
            f.read(10)
        return True
    except Exception:
        return False

def copy_image_to_output(source_path: Path, filename: str) -> Tuple[Path, Path]:
    """Copy image to backend and frontend directories."""
    
    backend_dir = get_backend_output_path("comic_panels")
    frontend_dir = get_frontend_public_path("comic_panels")

    # Ensure directories exist
    backend_dir.mkdir(parents=True, exist_ok=True)
    frontend_dir.mkdir(parents=True, exist_ok=True)

    backend_path = backend_dir / filename
    frontend_path = frontend_dir / filename

    # Copy with safe guards and informative prints
    try:
        shutil.copy2(source_path, backend_path)
        print(f"[image_utils] Copied to backend: {backend_path}")
    except Exception as e:
        print(f"[image_utils] Failed to copy to backend: {e}")

    try:
        shutil.copy2(source_path, frontend_path)
        print(f"[image_utils] Copied to frontend: {frontend_path}")
    except Exception as e:
        print(f"[image_utils] Failed to copy to frontend: {e}")

    return backend_path, frontend_path

def extract_panel_id(prompt: str) -> Optional[str]:
    """Extract panel number from prompt text."""
    match = re.search(r'panel\s*(\d+)', prompt.lower())
    if match:
        return f"panel_{match.group(1)}"
    return None

def update_registry_for_image(panel_id: str, filename: str, backend: bool, frontend: bool):
    """Update registry entry for a given panel."""
    verified = backend and frontend
    update_registry_entry(
        panel_id=panel_id,
        filename=filename,
        backend=backend,
        frontend=frontend,
        verified=verified
    )

def clean_temp_folder(folder_name: str, keep_recent: int = 0) -> None:
    """Deletes files in a Gemini temp folder, keeping only the most recent if specified."""
    gemini_root = Path(os.getenv("GEMINI_IMAGE_ROOT", "C:/Users/ninic/projects/Datacamp_projects/gemini-image-tutorial"))
    temp_dir = gemini_root / folder_name
    if not temp_dir.exists():
        print(f"🧹 Temp folder not found: {temp_dir}")
        return

    files = sorted(temp_dir.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)
    files_to_delete = files[keep_recent:] if keep_recent > 0 else files

    for file_path in files_to_delete:
        try:
            file_path.unlink()
            print(f"🧹 Deleted: {file_path}")
        except Exception as e:
            print(f"⚠️ Failed to delete {file_path}: {e}")

def clean_all_gemini_temp_folders() -> None:
    """Cleans all Gemini temp folders at once."""
    for folder in ["temp_multi_character", "temp_refinement_images"]:
        clean_temp_folder(folder)