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
        backend_output_path = Path("C:/Users/ninic/projects/CrewAI/comicbook/backend/output/comic_panels")
        frontend_panels_path = Path("C:/Users/ninic/projects/CrewAI/comicbook/frontend/public/comic_panels")
        return backend_output_path, frontend_panels_path

    def _extract_panel_paths(self, generation_results: str) -> Dict[int, str]:
        """Extract panel image paths from the generation results."""
        panel_paths = {}
        
        # Enhanced pattern matching for different formats
        # Format 1: "Panel 1: comic_panels/server_generated..."
        panel_pattern1 = r"Panel (\d+):\s*(comic_panels/[^\\s\n\r]+\.png)"
        matches1 = re.findall(panel_pattern1, generation_results, re.IGNORECASE)
        
        for match in matches1:
            panel_num = int(match[0])
            full_path = match[1].strip()
            # Extract just the filename
            filename = full_path.split('/')[-1]
            panel_paths[panel_num] = filename
            _dbg(f"Extracted Panel {panel_num}: {filename}")
        
        # Format 2: "Panel 1: [any path]/server_generated..."
        if not panel_paths:  # If first format didn't work, try second
            panel_pattern2 = r"Panel (\d+):\s*([^\n\r]+)"
            matches2 = re.findall(panel_pattern2, generation_results, re.IGNORECASE)
            
            for match in matches2:
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
        
        # Format 3: Look in registry for any recent panel files
        if len(panel_paths) < 6:
            _dbg("Trying registry-based detection for missing panels...")
            from .registry import read_registry
            registry = read_registry()
            
            # Look for panel entries in registry that might correspond to missing panels
            for entry_id, entry_data in registry.items():
                if 'server_generated' in entry_id and entry_data.get('verified'):
                    # Try to map to panel numbers based on creation order
                    panel_count = len(panel_paths) + 1
                    if panel_count <= 6 and panel_count not in panel_paths:
                        # The entry_id is the cleaned filename without extension
                        # The original cleaning was: re.sub(r'[^\w]', '_', filename.split('.')[0])
                        # So we need to reverse that transformation approximately
                        # Since the original had hyphens which became underscores, restore them
                        filename = entry_id.replace('_image_tutorial_', '-image-tutorial_') + '.png'
                        panel_paths[panel_count] = filename
                        _dbg(f"Registry Panel {panel_count}: {filename}")
        
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
        verified_from_registry = 0
        
        from .registry import get_panel_status, update_registry_entry

        # Validate each expected panel
        for panel_num in range(1, expected_panel_count + 1):
            # Skip validation if panel is already verified
            panel_id = f"panel_{panel_num}"
            registry_status = get_panel_status(panel_id)
            if registry_status.get('verified'):
                validation_results.append(f"- Panel {panel_num}: ✅ VERIFIED IN REGISTRY: {panel_paths.get(panel_num, 'cached')}")
                verified_from_registry += 1
                backend_files_found += 1
                frontend_files_found += 1
                continue
                
            if panel_num not in panel_paths:
                validation_results.append(f"- Panel {panel_num}: ❌ MISSING: No image path found in generation results")
                missing_panels.append(panel_num)
                continue
            
            filename = panel_paths[panel_num]
            file_check = self._check_file_existence(filename)
            
            # Update registry with current sync status
            update_registry_entry(
                panel_id=panel_id,
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
- Verified from registry cache: {verified_from_registry}/{expected_panel_count}
- Missing panels: {missing_panels if missing_panels else 'None'}

VALIDATION STATUS: {validation_status}

Summary:
- Total panels expected: {expected_panel_count}
- Panels with valid images: {total_valid_panels}
- Missing/invalid panels: {len(missing_panels)}
- Registry cache hits: {verified_from_registry}

{f"❌ CRITICAL: Comic assembly should NOT proceed - {len(missing_panels)} panels are missing!" if validation_status == "FAIL" else "✅ All panels validated - Comic ready for assembly!"}
"""
        
        _dbg(f"Validation complete: {validation_status} ({total_valid_panels}/{expected_panel_count} panels valid)")
        return report.strip()