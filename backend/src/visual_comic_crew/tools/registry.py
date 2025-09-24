import yaml
import os
from pathlib import Path

REGISTRY_PATH = Path("output/panel_registry.yaml")

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

def update_registry_entry(panel_id: str, filename: str = None, backend: bool = None, frontend: bool = None, verified: bool = None):
    """Update a single panel entry in the registry."""
    _ensure_registry_exists()
    registry = read_registry()
    
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
