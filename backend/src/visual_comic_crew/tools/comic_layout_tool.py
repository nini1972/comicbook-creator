from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Optional, Type
import os
import shutil
import glob
from datetime import datetime, timedelta

class ComicLayoutInput(BaseModel):
    panels: List[str] = Field(..., description="List of panel descriptions in order")
    dialogue: List[str] = Field(..., description="List of dialogue for each panel (same length as panels)")
    image_paths: Optional[List[str]] = Field(
        None,
        description="Optional list of image file paths corresponding 1:1 with panels."
    )

class ComicLayoutTool(BaseTool):
    name: str = "Comic Layout Designer"
    description: str = (
        "Takes lists of panel descriptions and matching dialogue lines and returns a markdown comic layout. "
        "Use after all panels and dialogue are finalized."
    )
    args_schema: Type[BaseModel] = ComicLayoutInput

    def _discover_recent_images(self, expected_count: int) -> Optional[List[str]]:
        """Discover recently generated images from the backend comic_panels directory."""
        try:
            # Look for images in the backend output directory
            comic_panels_dir = os.path.join("output", "comic_panels")
            if not os.path.exists(comic_panels_dir):
                print(f"[ComicLayoutTool] Directory not found: {comic_panels_dir}")
                return None
            
            # Get all PNG files sorted by modification time (newest first)
            pattern = os.path.join(comic_panels_dir, "*.png")
            image_files = glob.glob(pattern)
            
            if not image_files:
                print("[ComicLayoutTool] No PNG files found in comic_panels directory")
                return None
            
            # Sort by modification time (newest first)
            image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Filter to recent images (within last 10 minutes to catch current generation)
            recent_cutoff = datetime.now() - timedelta(minutes=10)
            recent_images = []
            
            for img_file in image_files:
                mod_time = datetime.fromtimestamp(os.path.getmtime(img_file))
                if mod_time >= recent_cutoff:
                    recent_images.append(img_file)
            
            if not recent_images:
                print("[ComicLayoutTool] No recent images found (within 10 minutes)")
                return None
            
            print(f"[ComicLayoutTool] Found {len(recent_images)} recent images")
            
            # Take the most recent images up to expected count
            selected_images = recent_images[:expected_count]
            
            # Pad with None if we don't have enough images
            while len(selected_images) < expected_count:
                selected_images.append(None)
            
            return selected_images
            
        except Exception as e:
            print(f"[ComicLayoutTool] Error discovering images: {e}")
            return None

    def _run(self, panels: List[str], dialogue: List[str], image_paths: Optional[List[str]] = None) -> str:
        if len(panels) != len(dialogue):
            return (
                f"Error: panels ({len(panels)}) and dialogue ({len(dialogue)}) count mismatch. "
                "They must be the same length."
            )
        if image_paths and len(image_paths) != len(panels):
            return (
                f"Error: image_paths ({len(image_paths)}) length must match panels ({len(panels)})."
            )
        
        # If no image paths provided, try to discover recent images automatically
        if not image_paths:
            print("[ComicLayoutTool] No image paths provided, attempting auto-discovery...")
            image_paths = self._discover_recent_images(len(panels))
            if image_paths:
                print(f"[ComicLayoutTool] Auto-discovered {len([p for p in image_paths if p])} images")
        
        # Copy images to frontend public directory if they exist
        frontend_image_paths = []
        if image_paths:
            frontend_public_dir = os.path.join("..", "frontend", "public", "comic_panels")
            os.makedirs(frontend_public_dir, exist_ok=True)
            
            for img_path in image_paths:
                if img_path:
                    filename = os.path.basename(img_path)
                    # Try to find the image in backend output directory
                    backend_img_path = None
                    if os.path.exists(img_path):
                        backend_img_path = img_path
                    else:
                        # Try backend output comic_panels directory
                        possible_path = os.path.join("output", "comic_panels", filename)
                        if os.path.exists(possible_path):
                            backend_img_path = possible_path
                    
                    if backend_img_path:
                        frontend_path = os.path.join(frontend_public_dir, filename)
                        try:
                            shutil.copy2(backend_img_path, frontend_path)
                            # Always use frontend path format
                            frontend_image_paths.append(f"/comic_panels/{filename}")
                            print(f"[ComicLayoutTool] Copied image to frontend: {frontend_path}")
                        except Exception as e:
                            print(f"[ComicLayoutTool] Failed to copy {backend_img_path}: {e}")
                            # Still use frontend path format even if copy failed
                            frontend_image_paths.append(f"/comic_panels/{filename}")
                    else:
                        print(f"[ComicLayoutTool] Image not found: {img_path}")
                        frontend_image_paths.append(None)
                else:
                    frontend_image_paths.append(None)
        
        layout_lines = ["# Comic Strip Layout", ""]
        for i, (panel, dial) in enumerate(zip(panels, dialogue), start=1):
            layout_lines.append(f"## Panel {i}")
            layout_lines.append(f"Description: {panel}")
            # Always prefer frontend paths when available
            if frontend_image_paths and i <= len(frontend_image_paths) and frontend_image_paths[i-1]:
                img_path = frontend_image_paths[i-1]
                layout_lines.append(f"![Panel {i}]({img_path})")
            elif image_paths and i <= len(image_paths) and image_paths[i-1]:
                # Fallback to original path but convert to frontend format
                filename = os.path.basename(image_paths[i-1])
                img_path = f"/comic_panels/{filename}"
                layout_lines.append(f"![Panel {i}]({img_path})")
            layout_lines.append(f"Dialogue: {dial}")
            layout_lines.append("")
        
        return "\n".join(layout_lines)
