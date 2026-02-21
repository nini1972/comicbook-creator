"""
Lore and Character Database Manager
Handles long-term memory for the comic generation process, allowing characters and story concepts
to persist across multiple chapters and runs.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.utils.path_utils import get_backend_output_path

class LoreDatabaseManager:
    """
    Manages the long-term lore and character database.
    This allows the story writer to maintain consistency across chapters.
    """
    
    def __init__(self):
        # Store the lore database in the knowledge folder or output folder
        self.db_file = get_backend_output_path("lore_database.yaml")
        self._ensure_db_file()
        
    def _ensure_db_file(self):
        """Create the database file with initial structure if it doesn't exist."""
        if not os.path.exists(self.db_file):
            initial_data = {
                'global_concept': '',
                'characters': {},
                'locations': {},
                'chapters_summary': [],
                'last_updated': datetime.now().isoformat()
            }
            self._write_db(initial_data)
            
    def _read_db(self) -> Dict[str, Any]:
        """Read the current database from file."""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error reading lore database file: {e}")
            return {}
            
    def _write_db(self, data: Dict[str, Any]):
        """Write database to file."""
        try:
            data['last_updated'] = datetime.now().isoformat()
            with open(self.db_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
        except Exception as e:
            print(f"Error writing lore database file: {e}")
            
    def update_global_concept(self, concept: str):
        """Update the overarching story concept."""
        data = self._read_db()
        data['global_concept'] = concept
        self._write_db(data)
        
    def get_global_concept(self) -> str:
        """Get the overarching story concept."""
        data = self._read_db()
        return data.get('global_concept', '')
        
    def add_or_update_character(self, name: str, description: str, visual_traits: str, role: str):
        """Add a new character or update an existing one."""
        data = self._read_db()
        if 'characters' not in data:
            data['characters'] = {}
            
        data['characters'][name] = {
            'description': description,
            'visual_traits': visual_traits,
            'role': role,
            'last_seen': datetime.now().isoformat()
        }
        self._write_db(data)
        
    def get_character(self, name: str) -> Optional[Dict[str, str]]:
        """Get details for a specific character."""
        data = self._read_db()
        return data.get('characters', {}).get(name)
        
    def get_all_characters(self) -> Dict[str, Dict[str, str]]:
        """Get all characters in the database."""
        data = self._read_db()
        return data.get('characters', {})
        
    def add_chapter_summary(self, chapter_num: str, title: str, summary: str):
        """Add a summary of a completed chapter."""
        data = self._read_db()
        if 'chapters_summary' not in data:
            data['chapters_summary'] = []
            
        # Check if chapter already exists and update it, otherwise append
        chapter_exists = False
        for chapter in data['chapters_summary']:
            if chapter.get('chapter_num') == chapter_num:
                chapter['title'] = title
                chapter['summary'] = summary
                chapter_exists = True
                break
                
        if not chapter_exists:
            data['chapters_summary'].append({
                'chapter_num': chapter_num,
                'title': title,
                'summary': summary,
                'date_added': datetime.now().isoformat()
            })
            
        self._write_db(data)
        
    def get_lore_summary(self) -> str:
        """Get a formatted string summarizing the entire lore database for the LLM context."""
        data = self._read_db()
        
        summary = "--- LORE DATABASE ---\n\n"
        
        concept = data.get('global_concept', '')
        if concept:
            summary += f"GLOBAL CONCEPT:\n{concept}\n\n"
            
        characters = data.get('characters', {})
        if characters:
            summary += "CHARACTERS:\n"
            for name, details in characters.items():
                summary += f"- {name} ({details.get('role', 'Unknown')}): {details.get('description', '')}\n"
                summary += f"  Visuals: {details.get('visual_traits', '')}\n"
            summary += "\n"
            
        chapters = data.get('chapters_summary', [])
        if chapters:
            summary += "PREVIOUS CHAPTERS:\n"
            for chapter in chapters:
                summary += f"- Chapter {chapter.get('chapter_num', '?')}: {chapter.get('title', 'Untitled')}\n"
                summary += f"  Summary: {chapter.get('summary', '')}\n"
                
        return summary

# Global instance
_lore_db = None

def get_lore_database() -> LoreDatabaseManager:
    """Get the global lore database instance."""
    global _lore_db
    if _lore_db is None:
        _lore_db = LoreDatabaseManager()
    return _lore_db
