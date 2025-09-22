# Implementation Roadmap: Evaluator & Orchestrator Integration

## Current System Analysis

### Existing Agent Workflow:
```
story_writer → visual_director → comic_layout
```

### File Structure:
- `config/agents.yaml` - Agent definitions
- `config/tasks.yaml` - Task definitions  
- `tools/` - Custom tools
- `src/visual_comic_crew/crew.py` - Main crew orchestration

## Phase 1: Quick Fix - Enhanced Evaluator Integration (Priority 1)

### 1.1 Add Evaluator Agent to agents.yaml
```yaml
evaluator:
  role: >
    Comic Panel Validation Specialist
  goal: >
    Validate that ALL comic panels referenced in the script have corresponding
    real image files in the filesystem. NEVER allow comics with missing images
    to proceed to assembly.
  backstory: >
    You are a meticulous quality assurance specialist who prevents broken comics
    by verifying every single panel image exists before final assembly. You have
    zero tolerance for fabricated filenames or missing images.
  verbose: true
  allow_delegation: false
```

### 1.2 Add Panel Validation Task to tasks.yaml
```yaml
panel_validation_task:
  description: >
    Validate that all comic panels referenced in the generated script have
    corresponding actual image files. Check:
    1. All panel numbers (1-6) are present
    2. All image file paths exist in the filesystem
    3. All images are accessible and not corrupted
    If ANY panels are missing, report the specific missing panels and STOP.
  expected_output: >
    A validation report listing:
    - ✅ VALIDATED panels with confirmed file paths
    - ❌ MISSING panels that need regeneration
    - OVERALL STATUS: PASS/FAIL
    - If FAIL: Specific action required
  agent: evaluator
  tools:
    - file_existence_checker
    - panel_validator
```

### 1.3 Create Validation Tools
```python
# tools/validation_tools.py
class FileExistenceChecker:
    def check_panel_images(self, comic_script: str) -> dict:
        """Check if all referenced image files actually exist"""
        # Parse comic script for image references
        # Check filesystem for each image
        # Return detailed validation results

class PanelValidator:
    def validate_completeness(self, comic_script: str, required_panels: int = 6) -> dict:
        """Validate that all required panels are present"""
        # Check panel numbering
        # Verify panel sequence
        # Return completeness status
```

## Phase 2: Orchestrator Integration (Priority 2)

### 2.1 Add Orchestrator Agent
```yaml
orchestrator:
  role: >
    Comic Generation Workflow Manager
  goal: >
    Manage the complete comic generation pipeline ensuring ALL panels are
    successfully generated through intelligent retry logic and quality control.
  backstory: >
    You are an experienced production manager who oversees complex creative
    workflows. You ensure no comic is released until every panel is perfect.
  verbose: true
  allow_delegation: true
```

### 2.2 Enhanced Workflow Tasks
```yaml
orchestrated_generation_task:
  description: >
    Orchestrate complete comic generation with validation and retry logic:
    1. Initial panel generation via Visual Director
    2. Validation via Evaluator
    3. Selective retry for failed panels (max 3 attempts)
    4. Final quality check before assembly
  expected_output: >
    Complete comic with ALL panels validated and ready for assembly
  agent: orchestrator
```

## Phase 3: Modified Crew Configuration

### 3.1 Update crew.py
```python
class VisualComicCrew:
    def __init__(self):
        self.agents_config = yaml.load(...)
        self.tasks_config = yaml.load(...)
        
    def create_agents(self):
        return {
            'story_writer': Agent(**self.agents_config['story_writer']),
            'visual_director': Agent(**self.agents_config['visual_director']),
            'evaluator': Agent(**self.agents_config['evaluator']),      # NEW
            'orchestrator': Agent(**self.agents_config['orchestrator']),  # NEW
            'comic_layout': Agent(**self.agents_config['comic_layout'])
        }
    
    def create_tasks(self, agents):
        tasks = [
            Task(**self.tasks_config['story_creation_task'], agent=agents['story_writer']),
            Task(**self.tasks_config['orchestrated_generation_task'], agent=agents['orchestrator']),  # MODIFIED
            Task(**self.tasks_config['panel_validation_task'], agent=agents['evaluator']),           # NEW
            Task(**self.tasks_config['comic_assembly_task'], agent=agents['comic_layout'])
        ]
        return tasks
```

### 3.2 Enhanced Task Dependencies
```python
# Set up task dependencies to ensure proper flow
story_task = tasks[0]
orchestrator_task = tasks[1]
validation_task = tasks[2] 
assembly_task = tasks[3]

# Dependencies
orchestrator_task.context = [story_task]
validation_task.context = [orchestrator_task]
assembly_task.context = [validation_task]
```

## Implementation Steps - Week 1

### Day 1-2: Evaluator Agent
1. ✅ Add evaluator agent to agents.yaml
2. ✅ Create panel validation task
3. ✅ Implement basic file existence checker
4. ✅ Test with current "good and evil" comic

### Day 3-4: Retry Logic
1. ✅ Add retry mechanism to Visual Director task
2. ✅ Implement selective panel regeneration
3. ✅ Add maximum retry limits
4. ✅ Test with known failure scenarios

### Day 5-7: Integration & Testing
1. ✅ Update crew.py with new agents
2. ✅ Modify task dependencies
3. ✅ End-to-end testing
4. ✅ Performance optimization

## Expected Results

### Immediate Benefits:
- ❌ No more 404 errors from missing images
- ✅ All comics will have complete panel sets
- ✅ Automatic retry for failed panels
- ✅ Clear validation reporting

### Quality Metrics:
- **Before**: 50% comics with missing panels
- **Target**: 100% comics with all panels validated
- **Retry Success Rate**: >90% failed panels recovered

## Risk Management

### Infinite Retry Prevention:
```python
MAX_RETRIES_PER_PANEL = 3
TOTAL_TIMEOUT = 600  # 10 minutes max
```

### Graceful Degradation:
- If validation fails after max retries, generate detailed error report
- Allow manual intervention with clear instructions
- Maintain partial success (e.g., 4/6 panels) rather than total failure

## Testing Strategy

### Unit Tests:
- File existence checker with known files
- Panel validator with various comic formats
- Retry logic with simulated failures

### Integration Tests:
- Full workflow with intentional failures
- Performance testing with complex comics
- Error recovery scenarios

### User Acceptance Tests:
- Generate comics with your existing test scripts
- Verify 100% panel completion rate
- Validate no 404 errors in frontend

## Next Steps for Implementation

1. **Immediate** (Today): Add evaluator agent configuration
2. **Tomorrow**: Implement file validation tools
3. **This Week**: Full integration with retry logic
4. **Next Week**: Comprehensive testing and optimization

Would you like me to start implementing the evaluator agent right away?