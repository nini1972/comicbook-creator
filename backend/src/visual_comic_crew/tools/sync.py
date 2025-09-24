"""
Sync handling utilities for comic panel generation
Provides polling logic to wait for file synchronization between backend and frontend
"""
import time
import os
from pathlib import Path
from typing import Dict, List, Tuple
from .registry import update_registry_entry

def _dbg(msg: str):
    print(f"[Sync] {msg}")

def poll_for_image_sync(panel_paths: Dict[str, str], 
                       backend_dir: str = "output/comic_panels",
                       frontend_dir: str = "frontend/public/comic_panels", 
                       retries: int = 3, 
                       delay: float = 2.5) -> Dict[str, Dict[str, bool]]:
    """
    Poll for image synchronization between backend and frontend directories.
    
    Args:
        panel_paths: Dict mapping panel_id to filename
        backend_dir: Backend directory path
        frontend_dir: Frontend directory path  
        retries: Number of polling attempts
        delay: Delay between polling attempts in seconds
        
    Returns:
        Dict mapping panel_id to sync status {'backend': bool, 'frontend': bool, 'verified': bool}
    """
    _dbg(f"Starting sync polling for {len(panel_paths)} panels")
    
    # Convert to absolute paths
    backend_path = Path("C:/Users/ninic/projects/CrewAI/comicbook/backend") / backend_dir
    frontend_path = Path("C:/Users/ninic/projects/CrewAI/comicbook") / frontend_dir
    
    sync_status = {}
    
    for attempt in range(retries):
        _dbg(f"Polling attempt {attempt + 1}/{retries}")
        
        for panel_id, filename in panel_paths.items():
            if panel_id in sync_status and sync_status[panel_id]['verified']:
                continue  # Skip already verified panels
                
            backend_file = backend_path / filename
            frontend_file = frontend_path / filename
            
            backend_exists = backend_file.exists() and backend_file.is_file()
            frontend_exists = frontend_file.exists() and frontend_file.is_file()
            verified = backend_exists and frontend_exists
            
            sync_status[panel_id] = {
                'backend': backend_exists,
                'frontend': frontend_exists, 
                'verified': verified
            }
            
            _dbg(f"  {panel_id}: backend={backend_exists}, frontend={frontend_exists}, verified={verified}")
        
        # Check if all panels are synced
        all_verified = all(status['verified'] for status in sync_status.values())
        if all_verified:
            _dbg("All panels verified - sync complete!")
            break
            
        if attempt < retries - 1:  # Don't sleep on last attempt
            _dbg(f"Waiting {delay}s before next poll...")
            time.sleep(delay)
    
    # Final status
    verified_count = sum(1 for status in sync_status.values() if status['verified'])
    _dbg(f"Sync polling complete: {verified_count}/{len(panel_paths)} panels verified")
    
    return sync_status

def update_panel_registry(sync_status: Dict[str, Dict[str, bool]]) -> None:
    """
    Update the panel registry with sync status results.
    Preserves existing verified entries unless explicitly overridden.
    
    Args:
        sync_status: Output from poll_for_image_sync
    """
    from .registry import get_panel_status
    
    _dbg(f"Updating registry with sync status for {len(sync_status)} panels")
    
    for panel_id, status in sync_status.items():
        # Check existing registry status
        existing_status = get_panel_status(panel_id)
        
        # If panel was already verified, don't downgrade unless we have better info
        if existing_status.get('verified') and not status['verified']:
            _dbg(f"Preserving verified status for {panel_id} (was already verified)")
            continue
            
        update_registry_entry(
            panel_id=panel_id,
            backend=status['backend'],
            frontend=status['frontend'], 
            verified=status['verified']
        )
    
    _dbg("Registry update complete")

def extract_panel_paths_from_generation_results(generation_results: str) -> Dict[str, str]:
    """
    Extract panel paths from generation results text.
    
    Args:
        generation_results: Text output from image generation
        
    Returns:
        Dict mapping panel_id to filename
    """
    import re
    
    panel_paths = {}
    
    # Look for patterns like "Panel 1: server_generated..." or "Panel 1: consistent_panel..."
    panel_pattern = r"Panel (\d+):\s*([^\n\r]+)"
    matches = re.findall(panel_pattern, generation_results, re.IGNORECASE)
    
    for match in matches:
        panel_num = int(match[0])
        path_text = match[1].strip()
        
        # Skip failed panels
        if "FAILED" in path_text.upper() or "ERROR" in path_text.upper():
            continue
            
        # Extract actual file path - look for both server_generated and consistent_panel patterns  
        path_match = re.search(r'(server_generated[^\s\]]+\.png|consistent_panel[^\s\]]+\.png)', path_text)
        if path_match:
            panel_id = f"panel_{panel_num}"
            panel_paths[panel_id] = path_match.group(1)
            continue
            
        # Also check for "Filename: xxx.png" pattern within this panel's text
        filename_match = re.search(r'Filename:\s*([^\s\n\r]+\.png)', path_text, re.IGNORECASE)
        if filename_match:
            panel_id = f"panel_{panel_num}"
            panel_paths[panel_id] = filename_match.group(1)
    
    return panel_paths