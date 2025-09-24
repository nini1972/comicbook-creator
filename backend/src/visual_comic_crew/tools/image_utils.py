import os
import time
import shutil
import re
from pathlib import Path
from typing import Optional, Tuple
from .registry import update_registry_entry

# Base directory for Gemini image server
GEMINI_BASE_DIR = r"C:\Users\ninic\projects\Datacamp_projects\gemini-image-tutorial"

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
    backend_dir = Path("output/comic_panels").resolve()
    frontend_dir = Path("../frontend/public/comic_panels").resolve()

    backend_dir.mkdir(parents=True, exist_ok=True)
    frontend_dir.mkdir(parents=True, exist_ok=True)

    backend_path = backend_dir / filename
    frontend_path = frontend_dir / filename

    shutil.copy2(source_path, backend_path)
    shutil.copy2(source_path, frontend_path)

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
