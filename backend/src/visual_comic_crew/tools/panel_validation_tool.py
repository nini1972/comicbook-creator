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

    def _normalize_filename(self, input_string: str) -> str:
        """
        Extract the actual filename from various tool output formats.
        
        Handles:
        - Full paths: "output/comic_panels/filename.png" -> "filename.png"
        - Descriptive text: "Image generated successfully. Filename: filename.png" -> "filename.png"
        - Direct filenames: "filename.png" -> "filename.png"
        """
        import re
        import os
        
        # Remove any path components, keeping only the filename
        filename = os.path.basename(input_string.strip())
        
        # If it's descriptive text with "Filename:" pattern, extract the filename
        filename_match = re.search(r'Filename:\s*([^\s\n\r]+)', input_string, re.IGNORECASE)
        if filename_match:
            filename = filename_match.group(1).strip()
            # Remove any remaining path components
            filename = os.path.basename(filename)
        
        # Clean up any remaining path separators or unwanted characters
        filename = filename.replace('\\', '').replace('/', '')
        
        return filename

    def _check_file_existence(self, filename: str) -> Dict[str, bool]:
        """Check if image file exists in backend and frontend locations."""
        # First normalize the filename to handle different input formats
        normalized_filename = self._normalize_filename(filename)
        
        backend_output_path, frontend_panels_path = self._get_paths()
        backend_file = backend_output_path / normalized_filename
        frontend_file = frontend_panels_path / normalized_filename
        
        return {
            'backend': backend_file.exists() and backend_file.is_file(),
            'frontend': frontend_file.exists() and frontend_file.is_file(),
            'backend_path': str(backend_file),
            'frontend_path': str(frontend_file),
            'normalized_filename': normalized_filename
        }

    def _run(self, panel_map: Dict[str, str], expected_panel_count: int = 6) -> str:
        """Validate all comic panels and return comprehensive validation report."""
        
        _dbg(f"Starting panel validation with panel_map: {panel_map}")
        print(f"PANEL_VALIDATION_TOOL_RECEIVED_MAP: {panel_map}")  # DEBUG
        
        # If panel_map is empty or None, try to extract from context
        if not panel_map:
            _dbg("Panel map is empty, attempting to extract from context...")
            # This should be handled by the agent framework, but let's add debug
            print("PANEL_VALIDATION_TOOL_CONTEXT_EXTRACTION_NEEDED")
        
        # Validate input
        if not panel_map or not isinstance(panel_map, dict):
            return "❌ ERROR: Invalid panel_map provided. Must be a dictionary mapping panel numbers to filenames."
        
        # Check for guessed/default filenames that indicate parsing failure
        # Only flag simple guessed patterns like "panel_1.png" but not complex generated filenames
        guessed_patterns = [r'^panel_\d+\.png$', r'^Panel_\d+\.png$', r'^panel\d+\.png$', r'^Panel\d+\.png$']
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
            normalized_filename = file_check['normalized_filename']
            
            # Update registry with current sync status and normalized filename
            update_registry_entry(
                panel_id=panel_id,
                filename=normalized_filename,
                backend=file_check['backend'],
                frontend=file_check['frontend'],
                verified=file_check['backend'] and file_check['frontend']
            )
            
            if file_check['backend']:
                backend_files_found += 1
            if file_check['frontend']:
                frontend_files_found += 1
            
            if file_check['backend'] and file_check['frontend']:
                validation_results.append(f"- Panel {panel_num}: ✅ VALID: {normalized_filename}")
            elif file_check['backend'] and not file_check['frontend']:
                validation_results.append(f"- Panel {panel_num}: ⚠️ BACKEND ONLY: {normalized_filename} (missing from frontend)")
                missing_panels.append(panel_num)
            elif not file_check['backend'] and file_check['frontend']:
                validation_results.append(f"- Panel {panel_num}: ⚠️ FRONTEND ONLY: {normalized_filename} (missing from backend)")
                missing_panels.append(panel_num)
            else:
                validation_results.append(f"- Panel {panel_num}: ❌ MISSING: {normalized_filename} (not found in either location)")
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