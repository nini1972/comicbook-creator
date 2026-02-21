"""
Lore Database Tool for CrewAI Agents
Provides agents with access to the long-term lore and character database.
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Type
import json
from src.utils.lore_database_manager import get_lore_database

class LoreDatabaseReadInput(BaseModel):
    action: str = Field(description="Action to perform: 'get_lore_summary', 'get_character', 'get_global_concept'")
    character_name: Optional[str] = Field(None, description="Character name (when action is 'get_character')")

class LoreDatabaseWriteInput(BaseModel):
    action: str = Field(description="Action to perform: 'update_global_concept', 'add_character', 'add_chapter_summary'")
    concept: Optional[str] = Field(None, description="Global story concept (when action is 'update_global_concept')")
    character_name: Optional[str] = Field(None, description="Character name (when action is 'add_character')")
    character_description: Optional[str] = Field(None, description="Character description (when action is 'add_character')")
    character_visuals: Optional[str] = Field(None, description="Character visual traits (when action is 'add_character')")
    character_role: Optional[str] = Field(None, description="Character role (when action is 'add_character')")
    chapter_num: Optional[str] = Field(None, description="Chapter number (when action is 'add_chapter_summary')")
    chapter_title: Optional[str] = Field(None, description="Chapter title (when action is 'add_chapter_summary')")
    chapter_summary: Optional[str] = Field(None, description="Chapter summary (when action is 'add_chapter_summary')")

class LoreDatabaseReaderTool(BaseTool):
    name: str = "LoreDatabaseReader"
    description: str = (
        "Read long-term story lore and character information from the database. "
        "Use this to maintain consistency across chapters and recall past events or characters. "
        "Actions: 'get_lore_summary', 'get_character' (requires character_name), 'get_global_concept'"
    )
    args_schema: Type[BaseModel] = LoreDatabaseReadInput

    def _run(self, action: str, character_name: Optional[str] = None) -> str:
        try:
            lore_db = get_lore_database()
            
            if action == "get_lore_summary":
                return lore_db.get_lore_summary()
                
            elif action == "get_character":
                if not character_name:
                    return "Character name is required for 'get_character' action."
                char = lore_db.get_character(character_name)
                if char:
                    return f"Character: {character_name}\nRole: {char.get('role')}\nDescription: {char.get('description')}\nVisuals: {char.get('visual_traits')}"
                return f"Character '{character_name}' not found in lore database."
                
            elif action == "get_global_concept":
                concept = lore_db.get_global_concept()
                return f"Global Concept: {concept}" if concept else "No global concept set yet."
                
            else:
                return f"Unknown action: {action}. Available actions: get_lore_summary, get_character, get_global_concept"
                
        except Exception as e:
            return f"Error reading lore database: {str(e)}"

class LoreDatabaseWriterTool(BaseTool):
    name: str = "LoreDatabaseWriter"
    description: str = (
        "Write long-term story lore and character information to the database. "
        "Use this to save new characters, update the global concept, or summarize a completed chapter. "
        "Actions: 'update_global_concept', 'add_character', 'add_chapter_summary'"
    )
    args_schema: Type[BaseModel] = LoreDatabaseWriteInput

    def _run(self, action: str, concept: Optional[str] = None, 
             character_name: Optional[str] = None, character_description: Optional[str] = None, 
             character_visuals: Optional[str] = None, character_role: Optional[str] = None,
             chapter_num: Optional[str] = None, chapter_title: Optional[str] = None, chapter_summary: Optional[str] = None) -> str:
        try:
            lore_db = get_lore_database()
            
            if action == "update_global_concept":
                if not concept:
                    return "Concept is required for 'update_global_concept' action."
                lore_db.update_global_concept(concept)
                return "Global concept updated successfully."
                
            elif action == "add_character":
                if not character_name or not character_description or not character_visuals:
                    return "Name, description, and visuals are required for 'add_character' action."
                role = character_role or "Supporting Character"
                lore_db.add_or_update_character(character_name, character_description, character_visuals, role)
                return f"Character '{character_name}' added/updated successfully."
                
            elif action == "add_chapter_summary":
                if not chapter_num or not chapter_title or not chapter_summary:
                    return "Chapter number, title, and summary are required for 'add_chapter_summary' action."
                lore_db.add_chapter_summary(chapter_num, chapter_title, chapter_summary)
                return f"Summary for Chapter {chapter_num} added successfully."
                
            else:
                return f"Unknown action: {action}. Available actions: update_global_concept, add_character, add_chapter_summary"
                
        except Exception as e:
            return f"Error writing to lore database: {str(e)}"

# Create tool instances
lore_database_reader = LoreDatabaseReaderTool()
lore_database_writer = LoreDatabaseWriterTool()
