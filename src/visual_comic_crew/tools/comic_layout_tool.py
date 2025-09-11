from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List

class ComicLayoutInput(BaseModel):
    panels: List[str] = Field(..., description="List of panel descriptions")
    dialogue: List[str] = Field(..., description="List of dialogue for each panel")

class ComicLayoutTool(BaseTool):
    name: str = "Comic Layout Designer"
    description: str = "Arrange comic panels into a layout with dialogue"
    args_schema: ComicLayoutInput

    def _run(self, panels: List[str], dialogue: List[str]) -> str:
        # Simple layout generation
        layout = "# Comic Strip Layout\n\n"
        for i, (panel, dial) in enumerate(zip(panels, dialogue), 1):
            layout += f"## Panel {i}\n"
            layout += f"Description: {panel}\n"
            layout += f"Dialogue: {dial}\n\n"
        return layout
