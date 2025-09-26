from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.gemini_image_tool import GeminiImageTool
from .tools.comic_layout_tool import ComicLayoutTool
from .tools.character_consistency_tool import CharacterConsistencyTool
from .tools.multi_character_scene_tool import MultiCharacterSceneTool
from .tools.image_refinement_tool import ImageRefinementTool
from .tools.orchestrator_tools import WorkflowControlTool, RetryManagerTool, StatusTrackerTool, CleanupTool
from .tools.panel_validation_tool import PanelValidationTool
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
        super().__init__()
        print("DEBUG: VisualComicCrew __init__ called")

    @agent
    def story_writer(self) -> Agent:
        print("DEBUG: Creating story_writer agent")
        agent = Agent(
            config=self.agents_config['story_writer'],
            verbose=True,
            multimodal=True
        )
        print(f"DEBUG: story_writer agent created with LLM: {agent.llm}")
        return agent

    @agent
    def visual_director(self) -> Agent:
        print("DEBUG: Creating visual_director agent")
        agent = Agent(
            config=self.agents_config['visual_director'],
            verbose=True,
            multimodal=True,
            tools=[GeminiImageTool(), CharacterConsistencyTool(), MultiCharacterSceneTool(), ImageRefinementTool()]
        )
        print(f"DEBUG: visual_director agent created with LLM: {agent.llm}")
        return agent

    @agent
    def evaluator(self) -> Agent:
        print("DEBUG: Creating evaluator agent")
        try:
            agent = Agent(
                config=self.agents_config['evaluator'],
                verbose=True,
                multimodal=True,
                tools=[PanelValidationTool()]
            )
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
        agent = Agent(
            config=self.agents_config['orchestrator'],
            verbose=True,
            multimodal=True,
            tools=[WorkflowControlTool(), RetryManagerTool(), StatusTrackerTool(), CleanupTool()]
        )
        print(f"DEBUG: orchestrator agent created with LLM: {agent.llm}")
        return agent

    @agent
    def comic_assembler(self) -> Agent:
        print("DEBUG: Creating comic_assembler agent")
        cfg = self.agents_config.get('comic_assembler')
        print(f"DEBUG: comic_assembler config keys: {list(cfg.keys()) if cfg else 'MISSING'}")
        try:
            agent = Agent(
                config=cfg,
                multimodal=True,
                tools=[ComicLayoutTool()],
                verbose=True
            )
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
    def orchestrated_generation_task(self) -> Task:
        print("DEBUG: Creating orchestrated_generation_task")
        return Task(
            config=self.tasks_config['orchestrated_generation_task']
        )

    @task
    def image_generation_task(self) -> Task:
        print("DEBUG: Creating image_generation_task")
        return Task(
            config=self.tasks_config['image_generation_task']
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

