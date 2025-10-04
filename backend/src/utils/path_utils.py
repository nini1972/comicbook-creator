from pathlib import Path
import inspect


def get_repo_root() -> Path:
    """Dynamically find the repo root by locating sibling 'backend' and 'frontend' folders."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "backend").exists() and (parent / "frontend").exists():
            return parent
    # Fallback: assume 3 levels up from utils
    return current.parents[3]
    print(f"[PathUtils] Repo root resolved to: {get_repo_root()}")

def get_output_path(subfolder: str = "") -> Path:
    """Returns the path to the global output folder under repo root."""
    return get_repo_root() / "output" / subfolder

def get_frontend_public_path(subfolder: str = "") -> Path:
    """Returns the path to the frontend public folder."""
    return get_repo_root() / "frontend" / "public" / subfolder

def get_backend_output_path(subfolder: str = "") -> Path:
    """Returns the path to the backend output folder."""
    return get_repo_root() / "backend" / "output" / subfolder

def get_registry_path() -> Path:
    return get_backend_output_path("panel_registry.yaml")   #"registry/panel_registry.yaml" if later move to subfolder registry