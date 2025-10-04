from pathlib import Path
from typing import List, Tuple, Type
from PIL import Image
from pydantic import BaseModel
from crewai.tools import BaseTool

from src.utils.panel_registry_inspector_utils import inspect_panel_registry
from src.utils.registry_utils import read_registry

def _dbg(msg: str):
    print(f"[PanelRegistryInspectorTool] {msg}")

class PanelRegistryInspectorSchema(BaseModel):
    image_paths: List[str]
    dialogue: List[str]

class PanelRegistryInspectorTool(BaseTool):
    name: str = "PanelRegistryInspectorTool"
    description: str = "Inspects panel image paths and validates readability and alignment with dialogue"
    args_schema: Type[PanelRegistryInspectorSchema] = PanelRegistryInspectorSchema

    @staticmethod
    def verify_image(path: Path) -> bool:
        try:
            with Image.open(path) as img:
                img.verify()
            return True
        except Exception:
            return False



    def _run(self, image_paths: List[str], dialogue: List[str]) -> str:
        # First, try to get panel information from registry
        try:
            registry = read_registry()
            _dbg(f"Registry data: {registry}")
            
            # Always build image_paths from registry to ensure we're using verified data
            image_paths = []
            panel_count = 0
            
            # Check all 6 panels
            for i in range(1, 7):
                panel_id = f"panel_{i}"
                if panel_id in registry:
                    panel_data = registry[panel_id]
                    if panel_data.get('verified', False) and 'filename' in panel_data and panel_data['filename']:
                        # Construct full path to image
                        from src.utils.path_utils import get_backend_output_path
                        image_path = get_backend_output_path("comic_panels") / panel_data['filename']
                        image_paths.append(str(image_path))
                        panel_count += 1
                    else:
                        # Add None for unverified panels
                        image_paths.append(None)
                else:
                    # Add None for missing panels
                    image_paths.append(None)
            
            _dbg(f"Built image_paths from registry: {image_paths}")
            _dbg(f"Verified panels count: {panel_count}")
            
        except Exception as e:
            _dbg(f"Error reading registry: {e}")
            # If registry reading fails, continue with provided image_paths
            pass
        
        valid, report = inspect_panel_registry(image_paths, dialogue)
        return "\n".join(report)