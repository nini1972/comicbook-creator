from crewai.tools import BaseTool
from typing import Type, Dict, List, Union
from pydantic import BaseModel, Field
import json
from src.utils.registry_utils import read_registry

class VisualDirectorOutputFormatterSchema(BaseModel):
    """Input for VisualDirectorOutputFormatter."""
    action: str = Field(..., description="Action to perform: 'format_output' or 'get_panel_map'")

class VisualDirectorOutputFormatter(BaseTool):
    name: str = "Visual Director Output Formatter"
    description: str = (
        "Formats the Visual Director's output as a JSON object mapping panel numbers to actual filenames. "
        "This tool ensures the output matches the expected format for the image generation task."
    )
    args_schema: Type[BaseModel] = VisualDirectorOutputFormatterSchema

    def _run(self, action: str) -> str:
        """Format the Visual Director's output as a JSON object."""
        if action == "format_output":
            # Get panel information from registry
            try:
                registry = read_registry()
                panel_map = {}
                for panel_id, panel_data in registry.items():
                    if panel_id.startswith("panel_"):
                        panel_num = panel_id.split("_")[1]
                        if 'filename' in panel_data:
                            panel_map[panel_num] = panel_data['filename']
                
                # Return as JSON string
                return json.dumps(panel_map, indent=2)
            except Exception as e:
                return f"Error reading registry: {str(e)}"
        elif action == "get_panel_map":
            # Get panel information from registry
            try:
                registry = read_registry()
                panel_map = {}
                for panel_id, panel_data in registry.items():
                    if panel_id.startswith("panel_"):
                        panel_num = panel_id.split("_")[1]
                        if 'filename' in panel_data:
                            panel_map[panel_num] = panel_data['filename']
                
                return panel_map
            except Exception as e:
                return f"Error reading registry: {str(e)}"
        else:
            return f"Unknown action: {action}. Use 'format_output' or 'get_panel_map'."
