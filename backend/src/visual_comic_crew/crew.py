from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.gemini_image_tool import GeminiImageTool
from .tools.comic_layout_tool import ComicLayoutTool
from .tools.character_consistency_tool import CharacterConsistencyTool
from .tools.multi_character_scene_tool import MultiCharacterSceneTool
from .tools.image_refinement_tool import ImageRefinementTool
from .tools.orchestrator_tools import WorkflowControlTool, RetryManagerTool, StatusTrackerTool, CleanupTool
from .tools.panel_validation_tool import PanelValidationTool
from .tools.panel_registry_inspector_tool import PanelRegistryInspectorTool
from .tools.visual_director_output_formatter import VisualDirectorOutputFormatter
from .tools.story_parser_tool import StoryParserTool
from .tools.story_metadata_tool import (
    StoryMetadataReaderTool, 
    StoryMetadataWriterTool, 
    StoryMetadataLayoutTool,
    story_metadata_reader,
    story_metadata_writer,
    story_metadata_layout
)
import traceback    
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"DEBUG: Loaded environment variables from {env_path}")
except ImportError:
    print("DEBUG: python-dotenv not available, environment variables may not be loaded")

@CrewBase
class VisualComicCrew():
    """Visual AI Comic Strip Creation Crew"""
    
    def __init__(self):
        # Call the parent class constructor which handles the configuration loading
        super().__init__()
        
        # Add debug prints to check if configurations are loaded
        print("DEBUG: VisualComicCrew.__init__ called")
        print(f"DEBUG: agents_config loaded: {hasattr(self, 'agents_config') and self.agents_config is not None}")
        print(f"DEBUG: tasks_config loaded: {hasattr(self, 'tasks_config') and self.tasks_config is not None}")
        
        # Check if configurations are loaded, if not, log an error
        if not hasattr(self, 'agents_config') or self.agents_config is None:
            print("ERROR: agents_config is not loaded properly!")
        else:
            print(f"DEBUG: agents_config keys: {list(self.agents_config.keys())}")
            
        if not hasattr(self, 'tasks_config') or self.tasks_config is None:
            print("ERROR: tasks_config is not loaded properly!")
        else:
            print(f"DEBUG: tasks_config keys: {list(self.tasks_config.keys())}")

        # Clear the registry at the start of each run
        try:
            from src.utils.registry_utils import clear_registry
            clear_registry()
            print("DEBUG: Registry cleared at start of run")
        except Exception as e:
            print(f"WARNING: Could not clear registry: {e}")

    def _create_agent_with_fallback(self, cfg: dict, **kwargs):
        """
        Try to create an Agent with provided cfg. If creation fails due to
        model not found (Anthropic/Claude), attempt a safe fallback to OpenAI GPT-4o.
        """
        from crewai import Agent
        try:
            agent = Agent(config=cfg, **kwargs)
            return agent
        except Exception as e:
            print(f"WARNING: Agent creation failed with error: {e}")
            # Try a conservative fallback for Anthropic model issues (not found or overloaded)
            llm_val = None
            try:
                llm_val = cfg.get('llm') if isinstance(cfg, dict) else None
            except Exception:
                llm_val = None
            
            # Check for Anthropic/Claude related errors including overload
            error_str = str(e).lower()
            if llm_val and ("anthropic" in str(llm_val).lower() or "claude" in str(llm_val).lower()) or \
               any(keyword in error_str for keyword in ["anthropic", "claude", "overloaded", "overload", "internalservererror"]):
                print(f"INFO: Attempting fallback LLM for config llm={llm_val} -> openai/gpt-4o")
                try_cfg = dict(cfg)
                try_cfg['llm'] = 'openai/gpt-4o'
                try:
                    agent = Agent(config=try_cfg, **kwargs)
                    print("INFO: Agent created with fallback llm=openai/gpt-4o")
                    return agent
                except Exception as e2:
                    print(f"ERROR: Fallback agent creation also failed: {e2}")
                    raise
            # If not an anthropic/claude issue, re-raise original
            raise

    @agent
    def story_writer(self) -> Agent:
        print("DEBUG: Creating story_writer agent")
        agent_cfg = self.agents_config.get('story_writer', {})
        agent = self._create_agent_with_fallback(agent_cfg, verbose=True, multimodal=True,
                                               tools=[story_metadata_reader, story_metadata_writer])
        print(f"DEBUG: story_writer agent created with LLM: {agent.llm}")
        return agent

    @agent
    def visual_director(self) -> Agent:
        print("DEBUG: Creating visual_director agent")
        agent_cfg = self.agents_config.get('visual_director', {})
        agent = self._create_agent_with_fallback(agent_cfg, verbose=True, multimodal=True,
                                               tools=[StoryParserTool(), GeminiImageTool(), CharacterConsistencyTool(), MultiCharacterSceneTool(), ImageRefinementTool(), VisualDirectorOutputFormatter(), story_metadata_reader, story_metadata_writer])
        print(f"DEBUG: visual_director agent created with LLM: {agent.llm}")
        return agent

    @agent
    def evaluator(self) -> Agent:
        print("DEBUG: Creating evaluator agent")
        try:
            agent_cfg = self.agents_config.get('evaluator', {})
            agent = self._create_agent_with_fallback(agent_cfg, verbose=True, multimodal=True, tools=[PanelValidationTool()])
        except Exception as e:
            print("ERROR: Exception during evaluator Agent() construction")
            print("ERROR: ", e)
            import traceback
            traceback.print_exc()
            raise
        print(f"DEBUG: evaluator agent created with LLM: {agent.llm}")
        return agent

    @agent
    def orchestrator(self) -> Agent:
        print("DEBUG: Creating orchestrator agent")
        agent_cfg = self.agents_config.get('orchestrator', {})
        agent = self._create_agent_with_fallback(agent_cfg, verbose=True, multimodal=True,
                                               tools=[VisualDirectorOutputFormatter(), WorkflowControlTool(), RetryManagerTool(), StatusTrackerTool(), StoryParserTool(), CleanupTool(), story_metadata_reader, story_metadata_writer])
        print(f"DEBUG: orchestrator agent created with LLM: {agent.llm}")
        return agent


    @agent
    def panel_registry_inspector(self) -> Agent:
        print("DEBUG: Creating panel_registry_inspector agent")
        cfg = self.agents_config.get('panel_registry_inspector')
        print(f"DEBUG: panel_registry_inspector config keys: {list(cfg.keys()) if cfg else 'MISSING'}")
        try:
            agent = self._create_agent_with_fallback(cfg, multimodal=True, tools=[PanelRegistryInspectorTool(), VisualDirectorOutputFormatter(), StoryParserTool(), story_metadata_reader, story_metadata_writer], verbose=True)
        except Exception as e:
            print("ERROR: Exception during panel_registry_inspector Agent() construction")
            print("ERROR: ", e)
            traceback.print_exc()
            # Re-raise so upstream can surface the failure instead of hanging silently
            raise
        print(f"DEBUG: panel_registry_inspector agent created with LLM: {agent.llm}")
        return agent


    @agent
    def comic_assembler(self) -> Agent:
        print("DEBUG: Creating comic_assembler agent")
        cfg = self.agents_config.get('comic_assembler')
        print(f"DEBUG: comic_assembler config keys: {list(cfg.keys()) if cfg else 'MISSING'}")
        try:
            agent = self._create_agent_with_fallback(cfg, multimodal=True, tools=[ComicLayoutTool(), VisualDirectorOutputFormatter(), story_metadata_reader, story_metadata_writer, story_metadata_layout], verbose=True)
        except Exception as e:
            print("ERROR: Exception during comic_assembler Agent() construction")
            print("ERROR: ", e)
            traceback.print_exc()
            # Re-raise so upstream can surface the failure instead of hanging silently
            raise
        print(f"DEBUG: comic_assembler agent created with LLM: {agent.llm}")
        return agent

    @task
    def story_creation_task(self) -> Task:
        print("DEBUG: Creating story_creation_task")
        return Task(
            config=self.tasks_config['story_creation_task']
        )

    @task
    def image_generation_task(self) -> Task:
        print("DEBUG: Creating image_generation_task")
        return Task(
            config=self.tasks_config['image_generation_task']
        )

    @task
    def orchestrated_generation_task(self) -> Task:
        print("DEBUG: Creating orchestrated_generation_task")
        return Task(
            config=self.tasks_config['orchestrated_generation_task']
        )


    @task
    def panel_registry_inspection_task(self) -> Task:
        print("DEBUG: Creating panel_registry_inspection_task")
        return Task(
            config=self.tasks_config['panel_registry_inspection_task']
        )

    @task
    def panel_validation_task(self) -> Task:
        print("DEBUG: Creating panel_validation_task")
        print(f"DEBUG: panel_validation_task config: {self.tasks_config.get('panel_validation_task')}")
        try:
            task = Task(
                config=self.tasks_config['panel_validation_task']
            )
            print(f"DEBUG: panel_validation_task created: {task}")
            return task
        except Exception as e:
            print(f"ERROR: Exception in panel_validation_task: {e}")
            import traceback
            traceback.print_exc()
            raise

    @task
    def comic_assembly_task(self) -> Task:
        print("DEBUG: Creating comic_assembly_task")
        # Extra debug: print the config being used
        print(f"DEBUG: comic_assembly_task config: {self.tasks_config.get('comic_assembly_task')}")
        task = Task(
            config=self.tasks_config['comic_assembly_task']
        )
        print(f"DEBUG: comic_assembly_task created: {task}")
        return task
    


    @crew
    def crew(self) -> Crew:
        print("DEBUG: Creating crew instance")
        try:
            # Surface configs for debugging
            try:
                agent_keys = list(self.agents_config.keys()) if getattr(self, 'agents_config', None) else []
            except Exception:
                agent_keys = '<unavailable>'
            try:
                task_keys = list(self.tasks_config.keys()) if getattr(self, 'tasks_config', None) else []
            except Exception:
                task_keys = '<unavailable>'
            print(f"DEBUG: agents_config keys: {agent_keys}")
            print(f"DEBUG: tasks_config keys: {task_keys}")

            # Force evaluation of agents and tasks and log each one
            print("DEBUG: Enumerating agents to force creation...")
            try:
                agents_obj = self.agents
                print(f"DEBUG: self.agents type: {type(agents_obj)}")
                try:
                    print(f"DEBUG: self.agents repr: {repr(agents_obj)}")
                except Exception:
                    pass
                # Try common iteration patterns
                if hasattr(agents_obj, 'items'):
                    for k, v in agents_obj.items():
                        print(f"DEBUG: agent entry: {k} -> {v}")
                elif isinstance(agents_obj, (list, tuple, set)):
                    for idx, v in enumerate(agents_obj):
                        print(f"DEBUG: agent[{idx}] -> {v}")
                else:
                    print(f"DEBUG: agents object has attrs: {dir(agents_obj)[:20]}")
            except Exception as e:
                print(f"ERROR enumerating agents: {e}")

            print("DEBUG: Enumerating tasks to force creation...")
            try:
                tasks_obj = self.tasks
                print(f"DEBUG: self.tasks type: {type(tasks_obj)}")
                try:
                    print(f"DEBUG: self.tasks repr: {repr(tasks_obj)}")
                except Exception:
                    pass
                if hasattr(tasks_obj, 'items'):
                    for k, v in tasks_obj.items():
                        print(f"DEBUG: task entry: {k} -> {v}")
                elif isinstance(tasks_obj, (list, tuple, set)):
                    for idx, v in enumerate(tasks_obj):
                        print(f"DEBUG: task[{idx}] -> {v}")
                else:
                    print(f"DEBUG: tasks object has attrs: {dir(tasks_obj)[:20]}")
            except Exception as e:
                print(f"ERROR enumerating tasks: {e}")

            crew_instance = Crew(
                agents=self.agents,
                tasks=self.tasks,
                process=Process.sequential,
                verbose=True
            )
            print(f"DEBUG: Crew created with {len(crew_instance.agents)} agents and {len(crew_instance.tasks)} tasks")
            return crew_instance
        except Exception as e:
            print("ERROR: Exception during Crew() construction")
            print("ERROR:", e)
            traceback.print_exc()
            raise

    # Backwards compatibility helpers
    def kickoff(self, inputs: dict = None):
        """Compatibility: allow calling kickoff directly on the CrewBase-decorated class instance.

        This forwards to the underlying Crew instance's kickoff method.
        """
        print("DEBUG: VisualComicCrew.kickoff called - forwarding to crew().kickoff")
        return self.crew().kickoff(inputs=inputs or {})

    def run(self, inputs: dict = None):
        """Alias for kickoff to support older call sites that use `run` or `kickoff`.
        """
        print("DEBUG: VisualComicCrew.run called - forwarding to crew().kickoff")
        return self.kickoff(inputs=inputs or {})

###not to use 
#####if __name__ == "__main__":
    # Create an instance of the crew
    #####comic_crew = VisualComicCrew()
    
    # Define inputs for the comic generation
    #####inputs = {
        #####'topic': 'Cybersecurity Adventure'  # You can change this to any topic you want
    #####}
    
    # Execute the crew
    #####print("DEBUG: Starting comic crew execution...")
    ######result = comic_crew.kickoff(inputs=inputs)
    #####print("DEBUG: Comic crew execution completed!")
    ####print("Result:", result)
