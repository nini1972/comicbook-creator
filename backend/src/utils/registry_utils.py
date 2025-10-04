import yaml
from pathlib import Path
from src.utils.path_utils import get_backend_output_path

REGISTRY_PATH = get_backend_output_path("panel_registry.yaml")

def _ensure_registry_exists():
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(REGISTRY_PATH, 'w') as f:
            yaml.dump({}, f)

def read_registry() -> dict:
    _ensure_registry_exists()
    with open(REGISTRY_PATH, 'r') as f:
        return yaml.safe_load(f) or {}

def update_registry_entry(panel_id: str, filename: str = None, backend: bool = None, frontend: bool = None, verified: bool = None):
    """Update a single panel entry in the registry."""
    print("[Tool] Registry update triggered")
    _ensure_registry_exists()
    registry = read_registry()

    # Standardize panel_id format to always start with "panel_"
    if not panel_id.startswith("panel_"):
        panel_id = f"panel_{panel_id}"

    if panel_id not in registry:
        registry[panel_id] = {}

    if filename is not None:
        registry[panel_id]['filename'] = filename
    if backend is not None:
        registry[panel_id]['backend_synced'] = backend
    if frontend is not None:
        registry[panel_id]['frontend_synced'] = frontend
    if verified is not None:
        registry[panel_id]['verified'] = verified

    with open(REGISTRY_PATH, 'w') as f:
        yaml.dump(registry, f)

    status_parts = []
    if filename is not None:
        status_parts.append(f"filename={filename}")
    if backend is not None:
        status_parts.append(f"backend={backend}")
    if frontend is not None:
        status_parts.append(f"frontend={frontend}")
    if verified is not None:
        status_parts.append(f"verified={verified}")

    print(f"[Registry] Updated {panel_id}: {', '.join(status_parts)}")
    print(f"[Registry] Using path: {REGISTRY_PATH}")

def clear_registry():
    """Clear the registry by writing an empty dictionary to the file."""
    _ensure_registry_exists()
    with open(REGISTRY_PATH, 'w') as f:
        yaml.dump({}, f)
    print("[Registry] Cleared registry")
