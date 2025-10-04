import yaml
import os
from pathlib import Path
from src.utils.path_utils import get_backend_output_path,get_registry_path
from src.utils.registry_utils import update_registry_entry

REGISTRY_PATH = get_registry_path()

def _ensure_registry_exists():
    """Create registry file if it doesn't exist."""
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(REGISTRY_PATH, 'w') as f:
            yaml.dump({}, f)

def read_registry() -> dict:
    """Read the full panel registry."""
    _ensure_registry_exists()
    with open(REGISTRY_PATH, 'r') as f:
        return yaml.safe_load(f) or {}

def get_panel_status(panel_id: str) -> dict:
    """Get sync status for a specific panel."""
    registry = read_registry()
    return registry.get(panel_id, {
        'filename': None,
        'backend_synced': False,
        'frontend_synced': False,
        'verified': False
    })

def get_unverified_panels(expected_count: int = 6) -> list:
    """Return list of panel IDs that are not fully verified."""
    registry = read_registry()
    unverified = []
    for i in range(1, expected_count + 1):
        panel_id = f"panel_{i}"
        status = registry.get(panel_id, {})
        if not status.get('verified'):
            unverified.append(i)
    return unverified
