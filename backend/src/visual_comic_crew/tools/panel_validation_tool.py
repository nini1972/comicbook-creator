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
    panel_map: Dict[str, str] = Field(None, description="Optional dictionary mapping panel numbers (e.g., '1') to their generated image filenames. If not provided, will attempt to extract from context.")
    context_text: str = Field(None, description="Optional context text from image generation task to extract panel mappings from.")
    expected_panel_count: int = Field(6, description="Expected number of panels in the comic (default: 6).")

class PanelValidationTool(BaseTool):
    name: str = "Panel Validation Tool"
    description: str = (
        "Validates that all comic panels have corresponding actual image files. "
        "Checks backend and frontend folders for image existence and provides detailed validation report."
    )
    args_schema: Type[BaseModel] = PanelValidationToolSchema

    def _get_paths(self):
        """Get the paths for image validation, robust to repo location."""
        repo_root = Path(__file__).resolve().parents[4]
        backend_output_path = repo_root / "backend" / "output" / "comic_panels"
        frontend_panels_path = repo_root / "frontend" / "public" / "comic_panels"
        return backend_output_path, frontend_panels_path

    def _normalize_filename(self, input_string: str) -> str:
        _dbg(f"_normalize_filename input: {input_string}")
        filename = os.path.basename(str(input_string).strip())
        filename_match = re.search(r'Filename:\s*([^\s\n\r]+)', str(input_string), re.IGNORECASE)
        if filename_match:
            filename = filename_match.group(1).strip()
            filename = os.path.basename(filename)
        filename = filename.replace('\\', '').replace('/', '')
        _dbg(f"_normalize_filename result: {filename}")
        return filename

    def _check_file_existence(self, filename: str) -> dict:
        normalized_filename = self._normalize_filename(filename)
        backend_output_path, frontend_panels_path = self._get_paths()
        backend_file = backend_output_path / normalized_filename
        frontend_file = frontend_panels_path / normalized_filename
        _dbg(f"_check_file_existence: normalized={normalized_filename}, backend_path={backend_file}, frontend_path={frontend_file}")
        try:
            backend_exists = backend_file.exists() and backend_file.is_file()
        except Exception as e:
            backend_exists = False
            _dbg(f"_check_file_existence backend.exists() error: {e}")
        try:
            frontend_exists = frontend_file.exists() and frontend_file.is_file()
        except Exception as e:
            frontend_exists = False
            _dbg(f"_check_file_existence frontend.exists() error: {e}")
        return {
            'backend': backend_exists,
            'frontend': frontend_exists,
            'backend_path': str(backend_file),
            'frontend_path': str(frontend_file),
            'normalized_filename': normalized_filename
        }

    def _extract_panel_mapping(self, text: str) -> dict:
        import re, json
        mapping = {}
        json_pattern = r'\{[^{}]*"[^"]*"\s*:\s*"[^"]*"[^{}]*\}'
        json_matches = re.findall(json_pattern, text, re.DOTALL)
        _dbg(f"_extract_panel_mapping: found {len(json_matches)} json matches")
        for json_str in json_matches:
            try:
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        if isinstance(v, str) and v.strip():
                            mapping[str(k)] = v.strip()
            except json.JSONDecodeError:
                continue
        if not mapping:
            patterns = [
                r'panel\s*(\d+)[\s:]+([^\s\n\r]+(?:\.[a-zA-Z]{3,4}))',
                r'Panel\s*(\d+)[\s:]+([^\s\n\r]+(?:\.[a-zA-Z]{3,4}))',
                r'(\d+)[\s:]+([^\s\n\r]+(?:\.[a-zA-Z]{3,4}))',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                _dbg(f"_extract_panel_mapping: pattern {pattern} found {len(matches)} matches")
                for panel_num, filename in matches:
                    if filename and not filename.lower().startswith(('panel', 'Panel')):
                        mapping[panel_num] = filename
        _dbg(f"Extracted panel mapping: {mapping}")
        return mapping

    def _run(self, panel_map: dict = None, context_text: str = None, expected_panel_count: int = 6) -> str:
        _dbg(f"Starting panel validation with panel_map: {panel_map}")
        print(f"PANEL_VALIDATION_TOOL_RECEIVED_MAP: {panel_map}")
        if not panel_map:
            _dbg("Panel map is empty, attempting to extract from context...")
            if context_text:
                _dbg("PanelValidationTool: extracting mapping from context_text")
                panel_map = self._extract_panel_mapping(context_text)
            else:
                return "❌ ERROR: No panel_map or context_text provided."
        if not panel_map or not isinstance(panel_map, dict):
            return "❌ ERROR: Invalid panel_map provided. Must be a dictionary mapping panel numbers to filenames."
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
        try:
            from .registry import update_registry_entry
        except ImportError:
            def update_registry_entry(**kwargs): pass
        for panel_num in range(1, expected_panel_count + 1):
            panel_key = str(panel_num)
            panel_id = f"panel_{panel_key}"
            filename = panel_map.get(panel_key)
            _dbg(f"_run: checking panel {panel_num}, raw filename: {filename}")
            if not filename or "FAILED" in str(filename).upper():
                validation_results.append(f"- Panel {panel_num}: ❌ MISSING: Generation failed or no path provided. Reason: {filename or 'N/A'}")
                missing_panels.append(panel_num)
                update_registry_entry(panel_id=panel_id, verified=False, filename=None)
                continue
            file_check = self._check_file_existence(filename)
            _dbg(f"_run: file_check for panel {panel_num}: {file_check}")
            normalized_filename = file_check['normalized_filename']
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

