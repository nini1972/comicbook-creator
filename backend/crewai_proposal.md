For creating a visual AI comic strip using Gemini 2.5 Flash Image and CrewAI, here's the recommended project structure:

## Project Structure

```
visual-comic-crew/
├── .env
├── pyproject.toml
├── README.md
├── output/
│   ├── comic_panels/
│   ├── scripts/
│   └── final_comic.md
└── src/
    └── visual_comic_crew/
        ├── __init__.py
        ├── main.py
        ├── crew.py
        ├── tools/
        │   ├── __init__.py
        │   ├── gemini_image_tool.py
        │   └── comic_layout_tool.py
        └── config/
            ├── agents.yaml
            └── tasks.yaml
```

## Agent Configuration (agents.yaml)

```yaml
story_writer:
  role: >
    Comic Story Writer and Script Creator
  goal: >
    Create engaging comic storylines with detailed panel descriptions
    and dialogue for visual comic strips
  backstory: >
    You're a creative comic writer with expertise in visual storytelling.
    You excel at breaking down stories into panels with clear visual
    descriptions and compelling dialogue.
  llm: google/gemini-2.0-flash-exp

visual_director:
  role: >
    Visual Director and Image Generation Specialist
  goal: >
    Generate consistent comic panel images using Gemini 2.5 Flash
    and ensure visual continuity across the comic strip
  backstory: >
    You're a visual director specializing in comic art generation.
    You understand composition, character consistency, and visual
    storytelling techniques for comic strips.
  llm: google/gemini-2.0-flash-exp

comic_assembler:
  role: >
    Comic Layout Designer and Final Assembly Specialist
  goal: >
    Assemble individual panels into a cohesive comic strip layout
    with proper formatting and presentation
  backstory: >
    You're a comic layout specialist who arranges panels, adds
    speech bubbles, and creates the final comic presentation.
  llm: google/gemini-2.0-flash-exp
```

## Task Configuration (tasks.yaml)

```yaml
story_creation_task:
  description: >
    Create a comic story script for {topic} with:
    1. A compelling storyline with beginning, middle, and end
    2. 4-6 panel breakdown with detailed visual descriptions
    3. Character descriptions and dialogue for each panel
    4. Visual style guidelines and mood specifications
  expected_output: >
    A detailed comic script with panel-by-panel descriptions,
    character details, dialogue, and visual style notes
  agent: story_writer

image_generation_task:
  description: >
    Generate comic panel images based on the story script:
    1. Create consistent character designs across panels
    2. Generate each panel image using Gemini 2.5 Flash
    3. Ensure visual continuity and comic art style
    4. Maintain consistent lighting and color palette
  expected_output: >
    A collection of comic panel images with consistent style
    and character representation
  agent: visual_director
  context:
    - story_creation_task

comic_assembly_task:
  description: >
    Assemble the final comic strip:
    1. Arrange panels in proper comic layout
    2. Add speech bubbles and dialogue
    3. Include title and credits
    4. Create final presentation format
  expected_output: >
    A complete comic strip with assembled panels, dialogue,
    and professional presentation
  agent: comic_assembler
  context:
    - story_creation_task
    - image_generation_task
  output_file: output/final_comic.md
```

## Custom Tools

Create custom tools for Gemini integration and comic layout:

```python
# src/visual_comic_crew/tools/gemini_image_tool.py
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import google.generativeai as genai

class GeminiImageInput(BaseModel):
    prompt: str = Field(..., description="Image generation prompt")
    style: str = Field(default="comic book art", description="Art style")

class GeminiImageTool(BaseTool):
    name: str = "Gemini Image Generator"
    description: str = "Generate comic panel images using Gemini 2.5 Flash"
    args_schema: Type[BaseModel] = GeminiImageInput

    def _run(self, prompt: str, style: str = "comic book art") -> str:
        # Configure Gemini for image generation
        full_prompt = f"{style}, {prompt}, high quality, detailed"
        # Implementation for Gemini 2.5 Flash image generation
        # Return image URL or path
        pass
```

## Main Crew Implementation

```python
# src/visual_comic_crew/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import DallETool  # Can be replaced with custom Gemini tool
from .tools.gemini_image_tool import GeminiImageTool

@CrewBase
class VisualComicCrew():
    """Visual AI Comic Strip Creation Crew"""

    @agent
    def story_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['story_writer'],
            verbose=True
        )

    @agent
    def visual_director(self) -> Agent:
        return Agent(
            config=self.agents_config['visual_director'],
            verbose=True,
            tools=[GeminiImageTool()]  # Custom Gemini tool
        )

    @agent
    def comic_assembler(self) -> Agent:
        return Agent(
            config=self.agents_config['comic_assembler'],
            verbose=True
        )

    @task
    def story_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['story_creation_task']
        )

    @task
    def image_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['image_generation_task']
        )

    @task
    def comic_assembly_task(self) -> Task:
        return Task(
            config=self.tasks_config['comic_assembly_task'],
            output_file='output/final_comic.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
```

This structure provides specialized agents for story creation, visual generation with Gemini 2.5 Flash, and final comic assembly, following CrewAI's best practices for collaborative AI workflows.

```suggestions
(Build Your First Crew)[/en/guides/crews/first-crew]
(Tasks)[/en/concepts/tasks]
(Tools)[/en/concepts/tools]
```