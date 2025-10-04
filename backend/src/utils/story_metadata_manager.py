"""
Story Metadata Manager for Comic Generation
Handles centralized story data persistence and sharing between agents.
"""

import yaml
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.utils.path_utils import get_backend_output_path


class StoryMetadataManager:
    """
    Manages the centralized story metadata file that serves as the single source of truth
    for all comic generation agents. Provides methods for reading, writing, and updating
    story information including panel descriptions, dialogue, and image paths.
    """
    
    def __init__(self, story_id: Optional[str] = None):
        """
        Initialize the StoryMetadataManager.
        
        Args:
            story_id: Unique identifier for the story. If None, will use timestamp-based ID.
        """
        if story_id is None:
            story_id = f"story_{int(datetime.now().timestamp())}"
        
        self.story_id = story_id
        self.metadata_file = get_backend_output_path(f"story_metadata_{story_id}.yaml")
        self._ensure_metadata_file()
    
    def _ensure_metadata_file(self):
        """Create the metadata file with initial structure if it doesn't exist."""
        if not os.path.exists(self.metadata_file):
            initial_data = {
                'story_metadata': {
                    'story_id': self.story_id,
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'status': 'initialized',
                    'agents_completed': []
                },
                'story_content': {
                    'topic': '',
                    'full_story_text': '',
                    'panels': [],
                    'image_filenames': {}
                },
                'generation_log': []
            }
            self._write_metadata(initial_data)
    
    def _read_metadata(self) -> Dict[str, Any]:
        """Read the current metadata from file."""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error reading metadata file: {e}")
            return {}
    
    def _write_metadata(self, data: Dict[str, Any]):
        """Write metadata to file."""
        try:
            # Update last_updated timestamp
            if 'story_metadata' in data:
                data['story_metadata']['last_updated'] = datetime.now().isoformat()
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
        except Exception as e:
            print(f"Error writing metadata file: {e}")
    
    def set_topic(self, topic: str):
        """Set the story topic."""
        data = self._read_metadata()
        data['story_content']['topic'] = topic
        self._write_metadata(data)
    
    def get_topic(self) -> str:
        """Get the story topic."""
        data = self._read_metadata()
        return data.get('story_content', {}).get('topic', '')
    
    def set_full_story_text(self, story_text: str, agent_name: str = 'story_writer'):
        """Set the full story text and mark agent as completed."""
        data = self._read_metadata()
        data['story_content']['full_story_text'] = story_text
        
        # Log the update
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'action': 'set_full_story_text',
            'details': f'Story text set ({len(story_text)} characters)'
        }
        data['generation_log'].append(log_entry)
        
        # Mark agent as completed if not already
        if agent_name not in data['story_metadata']['agents_completed']:
            data['story_metadata']['agents_completed'].append(agent_name)
        
        self._write_metadata(data)
    
    def get_full_story_text(self) -> str:
        """Get the full story text."""
        data = self._read_metadata()
        return data.get('story_content', {}).get('full_story_text', '')
    
    def set_panels(self, panels: List[Dict[str, Any]], agent_name: str = 'story_writer'):
        """
        Set the panel descriptions and dialogue.
        
        Args:
            panels: List of panel objects with 'number', 'description', 'dialogue' fields
            agent_name: Name of the agent setting the panels
        """
        data = self._read_metadata()
        data['story_content']['panels'] = panels
        
        # Log the update
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'action': 'set_panels',
            'details': f'Set {len(panels)} panels'
        }
        data['generation_log'].append(log_entry)
        
        # Mark agent as completed if not already
        if agent_name not in data['story_metadata']['agents_completed']:
            data['story_metadata']['agents_completed'].append(agent_name)
        
        self._write_metadata(data)
    
    def get_panels(self) -> List[Dict[str, Any]]:
        """Get the panel descriptions and dialogue."""
        data = self._read_metadata()
        return data.get('story_content', {}).get('panels', [])
    
    def get_panel_by_number(self, panel_number: int) -> Optional[Dict[str, Any]]:
        """Get a specific panel by its number."""
        panels = self.get_panels()
        for panel in panels:
            if panel.get('number') == panel_number:
                return panel
        return None
    
    def set_image_filename(self, panel_number: int, filename: str, agent_name: str = 'visual_director'):
        """Set the image filename for a specific panel."""
        data = self._read_metadata()
        if 'image_filenames' not in data['story_content']:
            data['story_content']['image_filenames'] = {}
        
        data['story_content']['image_filenames'][str(panel_number)] = filename
        
        # Log the update
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'action': 'set_image_filename',
            'details': f'Panel {panel_number}: {filename}'
        }
        data['generation_log'].append(log_entry)
        
        self._write_metadata(data)
    
    def get_image_filename(self, panel_number: int) -> Optional[str]:
        """Get the image filename for a specific panel."""
        data = self._read_metadata()
        return data.get('story_content', {}).get('image_filenames', {}).get(str(panel_number))
    
    def get_all_image_filenames(self) -> Dict[str, str]:
        """Get all image filenames as a dictionary."""
        data = self._read_metadata()
        return data.get('story_content', {}).get('image_filenames', {})
    
    def mark_agent_completed(self, agent_name: str, details: str = ''):
        """Mark an agent as completed with optional details."""
        data = self._read_metadata()
        
        if agent_name not in data['story_metadata']['agents_completed']:
            data['story_metadata']['agents_completed'].append(agent_name)
        
        # Log the completion
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'action': 'agent_completed',
            'details': details
        }
        data['generation_log'].append(log_entry)
        
        self._write_metadata(data)
    
    def get_completed_agents(self) -> List[str]:
        """Get list of agents that have completed their tasks."""
        data = self._read_metadata()
        return data.get('story_metadata', {}).get('agents_completed', [])
    
    def is_agent_completed(self, agent_name: str) -> bool:
        """Check if a specific agent has completed its task."""
        return agent_name in self.get_completed_agents()
    
    def set_story_status(self, status: str):
        """Set the overall story generation status."""
        data = self._read_metadata()
        data['story_metadata']['status'] = status
        self._write_metadata(data)
    
    def get_story_status(self) -> str:
        """Get the current story generation status."""
        data = self._read_metadata()
        return data.get('story_metadata', {}).get('status', 'unknown')
    
    def get_generation_log(self) -> List[Dict[str, Any]]:
        """Get the full generation log."""
        data = self._read_metadata()
        return data.get('generation_log', [])
    
    def get_story_summary(self) -> Dict[str, Any]:
        """Get a summary of the current story state."""
        data = self._read_metadata()
        panels = self.get_panels()
        image_filenames = self.get_all_image_filenames()
        
        return {
            'story_id': self.story_id,
            'status': self.get_story_status(),
            'topic': self.get_topic(),
            'has_full_story': bool(self.get_full_story_text()),
            'panel_count': len(panels),
            'images_generated': len(image_filenames),
            'completed_agents': self.get_completed_agents(),
            'last_updated': data.get('story_metadata', {}).get('last_updated', ''),
            'metadata_file': self.metadata_file
        }
    
    def export_for_layout(self) -> Dict[str, Any]:
        """
        Export story data in format suitable for comic layout generation.
        
        Returns:
            Dictionary with panels, dialogue, and image_paths for ComicLayoutTool
        """
        panels = self.get_panels()
        image_filenames = self.get_all_image_filenames()
        
        # Extract panel descriptions and dialogue in order
        panel_descriptions = []
        dialogue_list = []
        image_paths = []
        
        for i in range(1, 7):  # Expecting 6 panels
            panel = self.get_panel_by_number(i)
            if panel:
                panel_descriptions.append(panel.get('description', ''))
                dialogue_list.append(panel.get('dialogue', ''))
                
                # Get image path
                image_filename = image_filenames.get(str(i))
                if image_filename:
                    # Construct full path to image
                    image_path = get_backend_output_path(f"comic_panels/{image_filename}")
                    image_paths.append(image_path)
                else:
                    image_paths.append(None)
            else:
                panel_descriptions.append('')
                dialogue_list.append('')
                image_paths.append(None)
        
        return {
            'panels': panel_descriptions,
            'dialogue': dialogue_list,
            'image_paths': image_paths,
            'story_text': self.get_full_story_text()
        }
    
    def cleanup(self):
        """Remove the metadata file (useful for cleanup after comic generation)."""
        try:
            if os.path.exists(self.metadata_file):
                os.remove(self.metadata_file)
                print(f"Cleaned up metadata file: {self.metadata_file}")
        except Exception as e:
            print(f"Error cleaning up metadata file: {e}")
    
    @classmethod
    def get_latest_story_id(cls) -> Optional[str]:
        """Find the most recent story metadata file and return its story ID."""
        try:
            output_dir = get_backend_output_path("")
            metadata_files = list(Path(output_dir).glob("story_metadata_*.yaml"))
            
            if not metadata_files:
                return None
            
            # Sort by modification time, get the newest
            latest_file = max(metadata_files, key=lambda f: f.stat().st_mtime)
            
            # Extract story ID from filename
            filename = latest_file.name
            if filename.startswith("story_metadata_") and filename.endswith(".yaml"):
                story_id = filename[15:-5]  # Remove prefix and suffix
                return story_id
            
            return None
        except Exception as e:
            print(f"Error finding latest story ID: {e}")
            return None
    
    @classmethod
    def load_latest(cls) -> Optional['StoryMetadataManager']:
        """Load the most recent story metadata manager."""
        story_id = cls.get_latest_story_id()
        if story_id:
            return cls(story_id)
        return None


def get_current_story_metadata() -> Optional[StoryMetadataManager]:
    """
    Convenience function to get the current story metadata manager.
    Tries to load the latest story or returns None if no active story found.
    """
    return StoryMetadataManager.load_latest()