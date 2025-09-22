from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.gemini_image_tool import GeminiImageTool
from .tools.comic_layout_tool import ComicLayoutTool
from .tools.character_consistency_tool import CharacterConsistencyTool
from .tools.orchestrator_tools import WorkflowControlTool, RetryManagerTool, StatusTrackerTool
from .tools.panel_validation_tool import PanelValidationTool
import traceback

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
            tools=[GeminiImageTool(), CharacterConsistencyTool()]
        )
        print(f"DEBUG: visual_director agent created with LLM: {agent.llm}")
        return agent

    @agent
    def evaluator(self) -> Agent:
        print("DEBUG: Creating evaluator agent")
        agent = Agent(
            config=self.agents_config['evaluator'],
            verbose=True,
            multimodal=True,
            tools=[PanelValidationTool()]
        )
        print(f"DEBUG: evaluator agent created with LLM: {agent.llm}")
        return agent

    @agent
    def orchestrator(self) -> Agent:
        print("DEBUG: Creating orchestrator agent")
        agent = Agent(
            config=self.agents_config['orchestrator'],
            verbose=True,
            multimodal=True,
            tools=[WorkflowControlTool(), RetryManagerTool(), StatusTrackerTool()]
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
        return Task(
            config=self.tasks_config['panel_validation_task']
        )

    @task
    def comic_assembly_task(self) -> Task:
        print("DEBUG: Creating comic_assembly_task")
        return Task(
            config=self.tasks_config['comic_assembly_task']
        )

    @crew
    def crew(self) -> Crew:
        print("DEBUG: Creating crew instance")
        crew_instance = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        print(f"DEBUG: Crew created with {len(crew_instance.agents)} agents and {len(crew_instance.tasks)} tasks")
        return crew_instance
