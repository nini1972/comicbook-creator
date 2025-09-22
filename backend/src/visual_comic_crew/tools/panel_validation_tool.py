from crewai.tools import BaseTool
from typing import Type, Dict, List
from pydantic import BaseModel, Field
import os
import re
from pathlib import Path

def _dbg(msg: str):
    print(f"[PanelValidationTool] {msg}")

class PanelValidationToolSchema(BaseModel):
    """Input for PanelValidationTool."""
    image_generation_results: str = Field(..., description="The complete output from the image generation task containing panel results and image paths.")
    expected_panel_count: int = Field(6, description="Expected number of panels in the comic (default: 6).")

class PanelValidationTool(BaseTool):
    name: str = "Panel Validation Tool"
    description: str = (
        "Validates that all comic panels have corresponding actual image files. "
        "Checks backend and frontend folders for image existence and provides detailed validation report."
    )
    args_schema: Type[BaseModel] = PanelValidationToolSchema

    def _get_paths(self):
        """Get the paths for image validation."""
        backend_output_path = Path("C:/Users/ninic/projects/CrewAI/comicbook/backend/output")
        frontend_panels_path = Path("C:/Users/ninic/projects/CrewAI/comicbook/frontend/public/comic_panels")
        return backend_output_path, frontend_panels_path

    def _extract_panel_paths(self, generation_results: str) -> Dict[int, str]:
        """Extract panel image paths from the generation results."""
        panel_paths = {}
        
        # Look for patterns like "Panel 1: output\server_generated..." or "Panel 1: [path]"
        panel_pattern = r"Panel (\d+):\s*([^\n\r]+)"
        matches = re.findall(panel_pattern, generation_results, re.IGNORECASE)
        
        for match in matches:
            panel_num = int(match[0])
            path_text = match[1].strip()
            
            # Skip failed panels
            if "FAILED" in path_text.upper():
                _dbg(f"Panel {panel_num} marked as FAILED: {path_text}")
                continue
                
            # Extract actual file path - look for server_generated patterns
            path_match = re.search(r'(server_generated[^\\s\]]+\.png)', path_text)
            if path_match:
                panel_paths[panel_num] = path_match.group(1)
                _dbg(f"Extracted Panel {panel_num}: {panel_paths[panel_num]}")
            else:
                _dbg(f"Could not extract valid path from Panel {panel_num}: {path_text}")
        
        return panel_paths

    def _check_file_existence(self, filename: str) -> Dict[str, bool]:
        """Check if image file exists in backend and frontend locations."""
        backend_output_path, frontend_panels_path = self._get_paths()
        backend_file = backend_output_path / filename
        frontend_file = frontend_panels_path / filename
        
        return {
            'backend': backend_file.exists() and backend_file.is_file(),
            'frontend': frontend_file.exists() and frontend_file.is_file(),
            'backend_path': str(backend_file),
            'frontend_path': str(frontend_file)
        }

    def _run(self, image_generation_results: str, expected_panel_count: int = 6) -> str:
        """Validate all comic panels and return comprehensive validation report."""
        
        _dbg("Starting panel validation...")
        
        # Extract panel paths from generation results
        panel_paths = self._extract_panel_paths(image_generation_results)
        
        validation_results = []
        missing_panels = []
        backend_files_found = 0
        frontend_files_found = 0
        
        # Validate each expected panel
        for panel_num in range(1, expected_panel_count + 1):
            if panel_num not in panel_paths:
                validation_results.append(f"- Panel {panel_num}: ❌ MISSING: No image path found in generation results")
                missing_panels.append(panel_num)
                continue
            
            filename = panel_paths[panel_num]
            file_check = self._check_file_existence(filename)
            
            if file_check['backend']:
                backend_files_found += 1
            if file_check['frontend']:
                frontend_files_found += 1
            
            if file_check['backend'] and file_check['frontend']:
                validation_results.append(f"- Panel {panel_num}: ✅ VALID: {filename}")
            elif file_check['backend'] and not file_check['frontend']:
                validation_results.append(f"- Panel {panel_num}: ⚠️ BACKEND ONLY: {filename} (missing from frontend)")
                missing_panels.append(panel_num)
            elif not file_check['backend'] and file_check['frontend']:
                validation_results.append(f"- Panel {panel_num}: ⚠️ FRONTEND ONLY: {filename} (missing from backend)")
                missing_panels.append(panel_num)
            else:
                validation_results.append(f"- Panel {panel_num}: ❌ MISSING: {filename} (not found in either location)")
                missing_panels.append(panel_num)
        
        # Generate validation report
        total_valid_panels = expected_panel_count - len(missing_panels)
        validation_status = "PASS" if len(missing_panels) == 0 else "FAIL"
        
        report = f"""
Panel Validation Results:
{chr(10).join(validation_results)}

File System Check:
- Backend files found: {backend_files_found}/{expected_panel_count}
- Frontend files found: {frontend_files_found}/{expected_panel_count}
- Valid panels (both locations): {total_valid_panels}/{expected_panel_count}
- Missing panels: {missing_panels if missing_panels else 'None'}

VALIDATION STATUS: {validation_status}

Summary:
- Total panels expected: {expected_panel_count}
- Panels with valid images: {total_valid_panels}
- Missing/invalid panels: {len(missing_panels)}

{f"❌ CRITICAL: Comic assembly should NOT proceed - {len(missing_panels)} panels are missing!" if validation_status == "FAIL" else "✅ All panels validated - Comic ready for assembly!"}
"""
        
        _dbg(f"Validation complete: {validation_status} ({total_valid_panels}/{expected_panel_count} panels valid)")
        return report.strip()