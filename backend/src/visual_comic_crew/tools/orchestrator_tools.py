from crewai.tools import BaseTool
from typing import Type, Dict, List, Any
from pydantic import BaseModel, Field
import time
import json

def _dbg(msg: str):
    print(f"[OrchestratorTool] {msg}")

class WorkflowControlSchema(BaseModel):
    """Input for WorkflowControlTool."""
    action: str = Field(..., description="Action to perform: 'delegate_generation', 'check_status', 'retry_failed_panels'")
    target_agent: str = Field(default="visual_director", description="Agent to delegate to (default: visual_director)")
    panel_numbers: List[int] = Field(default=[], description="Specific panel numbers to regenerate (for retry action)")
    story_context: str = Field(default="", description="Story context for generation")
    max_attempts: int = Field(default=3, description="Maximum retry attempts per panel")
    expected_panels: int = Field(default=6, description="Expected number of panels for status checking")

class RetryManagerSchema(BaseModel):
    """Input for RetryManagerTool."""
    failed_panels: List[int] = Field(..., description="List of panel numbers that failed generation")
    total_panels: int = Field(default=6, description="Total number of panels expected")
    current_attempt: int = Field(default=1, description="Current retry attempt number")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")

class WorkflowControlTool(BaseTool):
    name: str = "Workflow Control Tool"
    description: str = (
        "Controls comic generation workflow by delegating tasks to other agents, "
        "managing retry logic, and coordinating the overall generation process."
    )
    args_schema: Type[BaseModel] = WorkflowControlSchema

    def _run(self, action: str, target_agent: str = "visual_director", panel_numbers: List[int] = [], 
             story_context: str = "", max_attempts: int = 3, expected_panels: int = 6) -> str:
        """Execute workflow control actions."""
        
        _dbg(f"Executing action: {action}")
        
        if action == "delegate_generation":
            return self._delegate_generation(target_agent, story_context)
        elif action == "check_status":
            return self._check_generation_status(expected_panels)
        elif action == "retry_failed_panels":
            return self._retry_failed_panels(panel_numbers, story_context, max_attempts)
        else:
            return f"Unknown action: {action}. Available actions: delegate_generation, check_status, retry_failed_panels"

    def _delegate_generation(self, target_agent: str, story_context: str) -> str:
        """Delegate initial generation to target agent."""
        _dbg(f"Delegating generation to {target_agent}")
        
        # Example of how to call GeminiImageTool for each panel (pseudo-code)
        # Example: Parse story_context into scene_descriptions (pseudo-code)
        scene_descriptions = story_context.split('\n')  # Replace with your actual parsing logic

        panel_map = {}

        for idx, scene_description in enumerate(scene_descriptions, start=1):
            prompt = f"Panel {idx}: {scene_description.strip()}"
            # result = gemini_image_tool._run(prompt=prompt, base_image_paths=None)
            # For demonstration, let's mock the result:
            import time
            result = f"server_generated_gemini-image-tutorial_{int(time.time() * 1000)}.png"
            panel_map[str(idx)] = result

        # Now panel_map is ready for validation and registry updates
        _dbg(f"Generated panel_map: {panel_map}")

         # You can return this, store it, or pass it to the next step in your workflow
        return json.dumps(panel_map, indent=2)


        delegation_instruction = f"""
        GENERATION DELEGATION TO {target_agent.upper()}:

        Task: Generate ALL comic panels based on the story context below.

        Story Context:
        {story_context}

        Requirements:
        1. Generate ALL panels described in the story (typically 1-6)
        2. Use proper tool calls for each panel. For each panel, construct the prompt as: "Panel <panel_number>: <scene description>"
        3. Record actual returned image paths (no fabrication)
        4. Provide complete generation summary with success/failure status
        5. Continue with all panels even if some fail

        Report back with detailed results for each panel.
        """
        return delegation_instruction

    def _check_generation_status(self, expected_panels: int = 6) -> str:
        """Check status of current generation process by querying registry."""
        _dbg("Checking generation status via registry")

        from .registry import read_registry, get_unverified_panels

        try:
            registry = read_registry()
            unverified_panel_nums = get_unverified_panels(expected_panels)

            # Count verified panels
            verified_panels = []
            all_panels_status = []

            for i in range(1, expected_panels + 1):
                panel_id = f"panel_{i}"
                status = registry.get(panel_id, {})

                if status.get('verified'):
                    verified_panels.append(panel_id)
                else:
                    all_panels_status.append(f"{panel_id}: {status}")

            status_check = f"""
REGISTRY-BASED STATUS CHECK:

Overall Status:
- Expected panels: {expected_panels}
- Verified panels: {len(verified_panels)}/{expected_panels}
- Unverified panels: {len(unverified_panel_nums)}/{expected_panels}

Verified Panels: {verified_panels}
Unverified Panel Numbers: {unverified_panel_nums}

Detailed Status:
{chr(10).join(all_panels_status)}

Next Steps:
"""

            if not unverified_panel_nums:
                status_check += "✅ All panels verified! Ready for comic assembly."
            else:
                status_check += f"🔄 Generation needed for panels: {unverified_panel_nums}"

        except Exception as e:
            _dbg(f"Registry check failed: {e}")
            status_check = f"""
REGISTRY STATUS CHECK FAILED:

Error: {e}

Please check registry file at output/panel_registry.yaml
"""

        return status_check

    def _retry_failed_panels(self, panel_numbers: List[int], story_context: str, max_attempts: int) -> str:
        """Generate retry instructions for failed panels."""
        _dbg(f"Generating retry instructions for panels: {panel_numbers}")
        
        if not panel_numbers:
            return "No failed panels specified for retry."
        
        retry_instruction = f"""
RETRY GENERATION FOR FAILED PANELS:

Failed Panel Numbers: {panel_numbers}
Maximum Attempts: {max_attempts}

Story Context:
{story_context}

Instructions for Visual Director:
1. Focus ONLY on the failed panel numbers listed above
2. For each failed panel:
   - Extract the panel description from the story
   - Attempt generation using appropriate tools
   - Record actual returned paths (no fabrication)
   - If panel fails again, note the specific failure reason
3. Provide detailed retry results

Do NOT regenerate successful panels - only retry the failed ones.
Report back with panel-specific results.
"""
        return retry_instruction

class RetryManagerTool(BaseTool):
    name: str = "Retry Manager Tool"
    description: str = (
        "Manages retry logic for failed comic panels, tracks attempts, "
        "and determines when to stop retrying based on limits."
    )
    args_schema: Type[BaseModel] = RetryManagerSchema

    def _run(self, failed_panels: List[int], total_panels: int = 6, 
             current_attempt: int = 1, max_retries: int = 3) -> str:
        """Manage retry logic with registry-aware filtering."""
        
        _dbg(f"Managing retry for panels {failed_panels}, attempt {current_attempt}/{max_retries}")
        
        # Patch 2: Registry-Aware Retry Filtering
        from .registry import get_panel_status
        
        # Filter failed_panels to exclude verified ones  
        filtered_failed_panels = []
        registry_verified_panels = []
        
        for panel_num in failed_panels:
            panel_id = f"panel_{panel_num}"
            status = get_panel_status(panel_id)
            if not status.get('verified'):
                filtered_failed_panels.append(panel_num)
            else:
                registry_verified_panels.append(panel_num)
                _dbg(f"Panel {panel_num} already verified in registry - skipping retry")
        
        # Use filtered_failed_panels for retry logic
        actual_failed_panels = filtered_failed_panels
        
        _dbg(f"Filtered retry list: {len(actual_failed_panels)} panels need retry, {len(registry_verified_panels)} already verified")
        
        # Calculate retry status using filtered panels
        success_rate = ((total_panels - len(actual_failed_panels)) / total_panels) * 100
        remaining_attempts = max_retries - current_attempt
        
        # Determine action
        if not actual_failed_panels:
            action = "COMPLETE"
            status = "SUCCESS"
            message = "All panels successfully generated!"
        elif current_attempt >= max_retries:
            action = "STOP"
            status = "FAILED"
            message = f"Maximum retry attempts ({max_retries}) reached. Manual intervention required."
        else:
            action = "RETRY"
            status = "IN_PROGRESS"
            message = f"Retry attempt {current_attempt + 1} recommended for {len(actual_failed_panels)} failed panels."
        
        retry_report = f"""
RETRY MANAGEMENT REPORT (Registry-Aware):

Current Status: {status}
Recommended Action: {action}

Panel Analysis:
- Total panels: {total_panels}
- Originally failed panels: {failed_panels}
- Registry-verified panels: {registry_verified_panels}
- Actual failed panels requiring retry: {actual_failed_panels}
- Success rate: {success_rate:.1f}%
- Current attempt: {current_attempt}
- Remaining attempts: {remaining_attempts}

{message}

Registry Intelligence:
- Panels verified since last check: {registry_verified_panels}
- Panels still needing retry: {actual_failed_panels}

Next Steps:
{self._get_next_steps(action, actual_failed_panels, remaining_attempts)}
"""
        
        return retry_report

    def _get_next_steps(self, action: str, failed_panels: List[int], remaining_attempts: int) -> str:
        """Generate next steps based on retry status."""
        
        if action == "COMPLETE":
            return "✅ Proceed to panel validation and comic assembly."
        elif action == "STOP":
            return f"❌ Stop retries. Failed panels {failed_panels} require manual investigation."
        elif action == "RETRY":
            return f"🔄 Retry generation for panels {failed_panels}. {remaining_attempts} attempts remaining."
        else:
            return "⚠️ Unknown action. Review retry logic."

class StatusTrackerTool(BaseTool):
    name: str = "Status Tracker Tool" 
    description: str = (
        "Tracks overall generation progress, monitors resource usage, "
        "and provides detailed status reports for the orchestrator."
    )
    args_schema: Type[BaseModel] = RetryManagerSchema  # Reuse schema

    def _run(self, failed_panels: List[int], total_panels: int = 6, 
             current_attempt: int = 1, max_retries: int = 3) -> str:
        """Track and report generation status."""
        
        _dbg("Generating status report")
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        success_count = total_panels - len(failed_panels)
        failure_count = len(failed_panels)
        
        status_report = f"""
ORCHESTRATOR STATUS REPORT
Generated: {timestamp}

PROGRESS SUMMARY:
- Total panels required: {total_panels}
- Successfully generated: {success_count}
- Failed panels: {failure_count}
- Current retry attempt: {current_attempt}
- Max retry limit: {max_retries}

DETAILED STATUS:
- Success rate: {(success_count/total_panels)*100:.1f}%
- Failure rate: {(failure_count/total_panels)*100:.1f}%
- Attempts remaining: {max_retries - current_attempt}

FAILED PANELS: {failed_panels if failed_panels else "None"}

RECOMMENDATIONS:
{self._get_recommendations(failed_panels, current_attempt, max_retries)}
"""
        
        return status_report

    def _get_recommendations(self, failed_panels: List[int], current_attempt: int, max_retries: int) -> str:
        """Generate recommendations based on current status."""
        
        if not failed_panels:
            return "✅ All panels generated successfully. Proceed to validation."
        elif current_attempt >= max_retries:
            return "❌ Maximum retries reached. Consider manual intervention or parameter adjustment."
        else:
            return f"🔄 Retry recommended for {len(failed_panels)} failed panels."