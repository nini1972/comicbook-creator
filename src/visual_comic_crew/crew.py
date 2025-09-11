from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.gemini_image_tool import GeminiImageTool

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
            tools=[GeminiImageTool()]
        )
        print(f"DEBUG: visual_director agent created with LLM: {agent.llm}")
        return agent

    @agent
    def comic_assembler(self) -> Agent:
        print("DEBUG: Creating comic_assembler agent")
        agent = Agent(
            config=self.agents_config['comic_assembler'],
            multimodal=True,
            verbose=True
        )
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
    def comic_assembly_task(self) -> Task:
        print("DEBUG: Creating comic_assembly_task")
        return Task(
            config=self.tasks_config['comic_assembly_task'],
            output_file='output/final_comic.md'
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
