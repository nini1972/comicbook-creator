#!/usr/bin/env python3
"""
Script to fix missing comic panel images by copying them from the Gemini output directory
to both backend and frontend directories.
"""

import os
import shutil
import yaml
from pathlib import Path

# Define paths
GEMINI_OUTPUT_DIR = Path("C:/Users/ninic/projects/Datacamp_projects/gemini-image-tutorial/output")
BACKEND_PANELS_DIR = Path("backend/output/comic_panels")
FRONTEND_PANELS_DIR = Path("frontend/public/comic_panels")
REGISTRY_PATH = Path("backend/output/panel_registry.yaml")

def load_registry():
    """Load the panel registry."""
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}

def copy_missing_images():
    """Copy missing images from Gemini output to backend and frontend directories."""
    # Create directories if they don't exist
    BACKEND_PANELS_DIR.mkdir(parents=True, exist_ok=True)
    FRONTEND_PANELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load registry
    registry = load_registry()
    
    if not registry:
        print("❌ No registry found. Nothing to do.")
        return
    
    copied_count = 0
    missing_count = 0
    
    print("🔍 Checking for missing panel images...")
    
    for panel_id, panel_data in registry.items():
        if not panel_id.startswith("panel_"):
            continue
            
        if 'filename' not in panel_data:
            print(f"⚠️  No filename for {panel_id}")
            continue
            
        filename = panel_data['filename']
        gemini_path = GEMINI_OUTPUT_DIR / filename
        backend_path = BACKEND_PANELS_DIR / filename
        frontend_path = FRONTEND_PANELS_DIR / filename
        
        # Check if image exists in both locations
        backend_exists = backend_path.exists()
        frontend_exists = frontend_path.exists()
        
        if backend_exists and frontend_exists:
            print(f"✅ {panel_id}: Already exists in both locations")
            continue
            
        # Check if source image exists in Gemini output
        if not gemini_path.exists():
            print(f"❌ {panel_id}: Source image not found in Gemini output: {filename}")
            missing_count += 1
            continue
            
        # Copy to backend if missing
        if not backend_exists:
            try:
                shutil.copy2(gemini_path, backend_path)
                print(f"📁 Copied to backend: {filename}")
            except Exception as e:
                print(f"❌ Failed to copy to backend: {filename} - {e}")
                
        # Copy to frontend if missing
        if not frontend_exists:
            try:
                shutil.copy2(gemini_path, frontend_path)
                print(f"🌐 Copied to frontend: {filename}")
            except Exception as e:
                print(f"❌ Failed to copy to frontend: {filename} - {e}")
                
        copied_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   - Images copied: {copied_count}")
    print(f"   - Missing sources: {missing_count}")

def update_registry():
    """Update registry entries to reflect current file status."""
    registry = load_registry()
    
    if not registry:
        print("❌ No registry found. Nothing to update.")
        return
        
    updated_count = 0
    
    for panel_id, panel_data in registry.items():
        if not panel_id.startswith("panel_"):
            continue
            
        if 'filename' not in panel_data:
            continue
            
        filename = panel_data['filename']
        backend_path = BACKEND_PANELS_DIR / filename
        frontend_path = FRONTEND_PANELS_DIR / filename
        
        # Check current status
        backend_exists = backend_path.exists()
        frontend_exists = frontend_path.exists()
        verified = backend_exists and frontend_exists
        
        # Update registry if status has changed
        if (panel_data.get('backend_synced') != backend_exists or 
            panel_data.get('frontend_synced') != frontend_exists or 
            panel_data.get('verified') != verified):
            
            panel_data['backend_synced'] = backend_exists
            panel_data['frontend_synced'] = frontend_exists
            panel_data['verified'] = verified
            
            updated_count += 1
            print(f"📝 Updated registry for {panel_id}: backend={backend_exists}, frontend={frontend_exists}, verified={verified}")
    
    # Save updated registry
    if updated_count > 0:
        with open(REGISTRY_PATH, 'w') as f:
            yaml.dump(registry, f)
        print(f"💾 Registry updated with {updated_count} changes")
    else:
        print("📋 Registry is already up to date")

def main():
    """Main function."""
    print("🔧 Fixing Missing Comic Panel Images")
    print("=" * 40)
    
    copy_missing_images()
    print()
    update_registry()
    
    print("\n✅ Process completed!")

if __name__ == "__main__":
    main()