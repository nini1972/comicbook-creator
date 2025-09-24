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
    panel_map: Dict[str, str] = Field(..., description="A dictionary mapping panel numbers (e.g., '1') to their generated image filenames or 'FAILED' status.")
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
        backend_output_path = Path("C:/Users/ninic/projects/CrewAI/comicbook/backend/output/comic_panels")
        frontend_panels_path = Path("C:/Users/ninic/projects/CrewAI/comicbook/frontend/public/comic_panels")
        return backend_output_path, frontend_panels_path

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

    def _run(self, panel_map: Dict[str, str], expected_panel_count: int = 6) -> str:
        """Validate all comic panels and return comprehensive validation report."""
        
        _dbg(f"Starting panel validation with panel_map: {panel_map}")
        
        # Validate input
        if not panel_map or not isinstance(panel_map, dict):
            return "❌ ERROR: Invalid panel_map provided. Must be a dictionary mapping panel numbers to filenames."
        
        # Check for guessed/default filenames that indicate parsing failure
        guessed_patterns = ['panel_', 'Panel_', 'panel\d+\.png', 'Panel\d+\.png']
        for panel_num, filename in panel_map.items():
            if isinstance(filename, str):
                for pattern in guessed_patterns:
                    import re
                    if re.search(pattern, filename):
                        return f"❌ ERROR: Detected guessed filename '{filename}' for panel {panel_num}. This indicates the image generation task did not produce proper JSON output. Please check the visual director task output and ensure it contains actual generated filenames, not guessed ones."
        
        validation_results = []
        missing_panels = []
        backend_files_found = 0
        frontend_files_found = 0
        
        from .registry import update_registry_entry

        # Validate each expected panel
        for panel_num in range(1, expected_panel_count + 1):
            panel_key = str(panel_num)
            panel_id = f"panel_{panel_key}"
            
            filename = panel_map.get(panel_key)
            
            if not filename or "FAILED" in filename.upper():
                validation_results.append(f"- Panel {panel_num}: ❌ MISSING: Generation failed or no path provided. Reason: {filename or 'N/A'}")
                missing_panels.append(panel_num)
                update_registry_entry(panel_id=panel_id, verified=False, filename=None)
                continue
            
            file_check = self._check_file_existence(filename)
            
            # Update registry with current sync status and filename
            update_registry_entry(
                panel_id=panel_id,
                filename=filename,
                backend=file_check['backend'],
                frontend=file_check['frontend'],
                verified=file_check['backend'] and file_check['frontend']
            )
            
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