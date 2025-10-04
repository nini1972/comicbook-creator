#!/usr/bin/env python3
"""
Script to copy specific comic panel images from backend to frontend directories.
"""

import os
import shutil
from pathlib import Path

# Define paths
BACKEND_PANELS_DIR = Path("backend/output/comic_panels")
FRONTEND_PANELS_DIR = Path("frontend/public/comic_panels")

# Specific files to copy (these exist in backend but not frontend)
FILES_TO_COPY = [
    "panel_001_server_generated_gemini-image-tutorial_1759440164883.png",
    "consistent_panel_002_captain aurora_1759440190784.png",
    "panel_003_server_generated_gemini-image-tutorial_1759440230320.png",
    "panel_004_server_generated_gemini-image-tutorial_1759440245320.png",
    "multi_char_panel_005_captain_aurora_police_officer_1759440289133.png",
    "panel_006_server_generated_gemini-image-tutorial_1759440304641.png"
]

def copy_backend_to_frontend():
    """Copy specific images from backend to frontend directory."""
    # Create frontend directory if it doesn't exist
    FRONTEND_PANELS_DIR.mkdir(parents=True, exist_ok=True)
    
    copied_count = 0
    missing_count = 0
    
    print("🔍 Copying panel images from backend to frontend...")
    
    for filename in FILES_TO_COPY:
        backend_path = BACKEND_PANELS_DIR / filename
        frontend_path = FRONTEND_PANELS_DIR / filename
        
        # Check if source image exists in backend
        if not backend_path.exists():
            print(f"❌ Source image not found in backend: {filename}")
            missing_count += 1
            continue
            
        # Copy to frontend
        try:
            shutil.copy2(backend_path, frontend_path)
            print(f"🌐 Copied to frontend: {filename}")
            copied_count += 1
        except Exception as e:
            print(f"❌ Failed to copy to frontend: {filename} - {e}")
            missing_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   - Images copied: {copied_count}")
    print(f"   - Missing sources: {missing_count}")

def main():
    """Main function."""
    print("🔧 Copying Backend Images to Frontend")
    print("=" * 40)
    
    copy_backend_to_frontend()
    
    print("\n✅ Process completed!")

if __name__ == "__main__":
    main()