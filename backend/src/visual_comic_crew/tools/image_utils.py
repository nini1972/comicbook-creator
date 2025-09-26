import os
import time
import shutil
import re
from pathlib import Path
from typing import Optional, Tuple,List
from .registry import update_registry_entry

# Base directory for Gemini image server
GEMINI_BASE_DIR = r"C:\Users\ninic\projects\Datacamp_projects\gemini-image-tutorial"

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
    # Determine repository root by climbing up until a sibling `frontend` folder is found.
    start = Path(__file__).resolve()
    repo_root = start
    while repo_root != repo_root.parent:
        if (repo_root / "frontend").exists() and (repo_root / "backend").exists():
            break
        repo_root = repo_root.parent

    # Fallback to parent-of-backend if we didn't find an obvious repo root
    if (repo_root / "frontend").exists():
        base = repo_root
    else:
        # try one level up from backend (handles the common workspace layout)
        base = Path(__file__).parents[3].parent if len(Path(__file__).parents) >= 4 else Path(__file__).parents[3]

    backend_dir = base / "backend" / "output" / "comic_panels"
    frontend_dir = base / "frontend" / "public" / "comic_panels"

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

