from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
import re

class StoryParserToolSchema(BaseModel):
    """Input for StoryParserTool."""
    story_text: str = Field(..., description="The story text to parse for panel descriptions and dialogue")
    action: str = Field(..., description="Action to perform: 'extract_panels' or 'extract_dialogue'")

class StoryParserTool(BaseTool):
    name: str = "StoryParserTool"
    description: str = (
        "Parses a comic story to extract panel descriptions and dialogue. "
        "Use this tool to extract the necessary information for the ComicLayoutTool."
    )
    args_schema: Type[BaseModel] = StoryParserToolSchema

    def _extract_panels(self, story_text: str) -> List[str]:
        """Extract panel descriptions from the story text."""
        panels = []
        
        # Look for patterns like "Panel 1:", "Panel 1)", "1.", etc.
        # This pattern looks for "Panel X:" or "Panel X." or "Panel X)" followed by content until the next panel or end
        panel_pattern = r'Panel\s+\d+[:\.].*?(?=\n\s*Panel\s+\d+[:\.]|\Z)'
        matches = re.findall(panel_pattern, story_text, re.DOTALL | re.IGNORECASE)
        
        if matches:
            for match in matches:
                # Clean up the panel text
                panel_text = re.sub(r'Panel\s+\d+[:\.]\s*', '', match, flags=re.IGNORECASE).strip()
                # Remove extra whitespace and newlines
                panel_text = re.sub(r'\s+', ' ', panel_text)
                panels.append(panel_text)
        else:
            # If no clear panel markers, try to split the story into 6 parts
            # This is a fallback approach
            sentences = re.split(r'[.!?]+', story_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            if len(sentences) >= 6:
                # Distribute sentences across 6 panels
                sentences_per_panel = max(1, len(sentences) // 6)
                for i in range(6):
                    start = i * sentences_per_panel
                    end = min((i + 1) * sentences_per_panel, len(sentences))
                    panel_text = '. '.join(sentences[start:end])
                    if panel_text:
                        panel_text += '.'
                    panels.append(panel_text)
            else:
                # If we can't split properly, return the whole story as one panel
                panels = [story_text]
                
        # Ensure we have exactly 6 panels
        while len(panels) < 6:
            panels.append("")
        return panels[:6]

    def _extract_dialogue(self, story_text: str) -> List[str]:
        """Extract dialogue from the story text."""
        # Look for dialogue patterns in quotes
        dialogue_pattern = r'["\u201c\u201d](.*?)["\u201d\u201c]'
        dialogues = re.findall(dialogue_pattern, story_text, re.DOTALL)
        
        # If no dialogue found, create empty dialogue for each panel
        if not dialogues:
            dialogues = [""] * 6
        else:
            # Ensure we have exactly 6 dialogue entries
            while len(dialogues) < 6:
                dialogues.append("")
            dialogues = dialogues[:6]
            
        return dialogues

    def _run(self, story_text: str, action: str) -> str:
        """Parse the story text and extract panel descriptions or dialogue."""
        try:
            if action == "extract_panels":
                panels = self._extract_panels(story_text)
                return panels
            elif action == "extract_dialogue":
                dialogues = self._extract_dialogue(story_text)
                return dialogues
            else:
                return f"Unknown action: {action}. Use 'extract_panels' or 'extract_dialogue'."
        except Exception as e:
            return f"Error parsing story: {str(e)}"