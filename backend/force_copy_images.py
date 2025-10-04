#!/usr/bin/env python3
"""
Script to force copy specific comic panel images from the Gemini output directory
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

# Specific files to copy
FILES_TO_COPY = [
    "panel_001_server_generated_gemini-image-tutorial_1759440164883.png",
    "consistent_panel_002_captain aurora_1759440190784.png",
    "panel_003_server_generated_gemini-image-tutorial_1759440230320.png",
    "panel_004_server_generated_gemini-image-tutorial_1759440245320.png",
    "multi_char_panel_005_captain_aurora_police_officer_1759440289133.png",
    "panel_006_server_generated_gemini-image-tutorial_1759440304641.png"
]

def force_copy_images():
    """Force copy specific images from Gemini output to backend and frontend directories."""
    # Create directories if they don't exist
    BACKEND_PANELS_DIR.mkdir(parents=True, exist_ok=True)
    FRONTEND_PANELS_DIR.mkdir(parents=True, exist_ok=True)
    
    copied_count = 0
    missing_count = 0
    
    print("🔍 Force copying specific panel images...")
    
    for filename in FILES_TO_COPY:
        gemini_path = GEMINI_OUTPUT_DIR / filename
        backend_path = BACKEND_PANELS_DIR / filename
        frontend_path = FRONTEND_PANELS_DIR / filename
        
        # Check if source image exists in Gemini output
        if not gemini_path.exists():
            print(f"❌ Source image not found in Gemini output: {filename}")
            missing_count += 1
            continue
            
        # Copy to backend
        try:
            shutil.copy2(gemini_path, backend_path)
            print(f"📁 Copied to backend: {filename}")
        except Exception as e:
            print(f"❌ Failed to copy to backend: {filename} - {e}")
            
        # Copy to frontend
        try:
            shutil.copy2(gemini_path, frontend_path)
            print(f"🌐 Copied to frontend: {filename}")
        except Exception as e:
            print(f"❌ Failed to copy to frontend: {filename} - {e}")
            
        copied_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   - Images copied: {copied_count}")
    print(f"   - Missing sources: {missing_count}")

def main():
    """Main function."""
    print("🔧 Force Copying Comic Panel Images")
    print("=" * 40)
    
    force_copy_images()
    
    print("\n✅ Process completed!")

if __name__ == "__main__":
    main()