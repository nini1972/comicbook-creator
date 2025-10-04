"""
Story Metadata Tool for CrewAI Agents
Provides agents with access to the centralized story metadata file.
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Type
import json
from src.utils.story_metadata_manager import StoryMetadataManager, get_current_story_metadata


class StoryMetadataReadInput(BaseModel):
    action: str = Field(description="Action to perform: 'get_topic', 'get_story_text', 'get_panels', 'get_panel', 'get_images', 'get_summary', 'get_status'")
    panel_number: Optional[int] = Field(None, description="Panel number (1-6) when action is 'get_panel'")


class StoryMetadataWriteInput(BaseModel):
    action: str = Field(description="Action to perform: 'set_topic', 'set_story_text', 'set_panels', 'set_image', 'mark_completed', 'set_status'")
    topic: Optional[str] = Field(None, description="Story topic (when action is 'set_topic')")
    story_text: Optional[str] = Field(None, description="Full story text (when action is 'set_story_text')")
    panels_json: Optional[str] = Field(None, description="JSON string of panels array (when action is 'set_panels')")
    panel_number: Optional[int] = Field(None, description="Panel number (when action is 'set_image')")
    image_filename: Optional[str] = Field(None, description="Image filename (when action is 'set_image')")
    agent_name: Optional[str] = Field(None, description="Agent name (when action is 'mark_completed')")
    status: Optional[str] = Field(None, description="Story status (when action is 'set_status')")
    details: Optional[str] = Field(None, description="Additional details for logging")


class StoryMetadataReaderTool(BaseTool):
    name: str = "StoryMetadataReader"
    description: str = (
        "Read story information from the centralized story metadata file. "
        "Use this to access story content, panel descriptions, image filenames, and generation status. "
        "Actions: 'get_topic', 'get_story_text', 'get_panels', 'get_panel' (requires panel_number), "
        "'get_images', 'get_summary', 'get_status'"
    )
    args_schema: Type[BaseModel] = StoryMetadataReadInput

    def _run(self, action: str, panel_number: Optional[int] = None) -> str:
        try:
            # Get current story metadata manager
            metadata_manager = get_current_story_metadata()
            if not metadata_manager:
                return "No active story metadata found. Story may not have been initialized yet."
            
            if action == "get_topic":
                topic = metadata_manager.get_topic()
                return f"Story Topic: {topic}" if topic else "No topic set yet."
            
            elif action == "get_story_text":
                story_text = metadata_manager.get_full_story_text()
                if story_text:
                    return f"Full Story Text:\n{story_text}"
                else:
                    return "No story text available yet."
            
            elif action == "get_panels":
                panels = metadata_manager.get_panels()
                if panels:
                    panels_info = []
                    for panel in panels:
                        panels_info.append(f"Panel {panel.get('number', 'Unknown')}: {panel.get('description', 'No description')}")
                        if panel.get('dialogue'):
                            panels_info.append(f"  Dialogue: {panel.get('dialogue')}")
                    return "\n".join(panels_info)
                else:
                    return "No panels available yet."
            
            elif action == "get_panel":
                if panel_number is None:
                    return "Panel number is required for 'get_panel' action."
                
                panel = metadata_manager.get_panel_by_number(panel_number)
                if panel:
                    result = f"Panel {panel_number}:\n"
                    result += f"Description: {panel.get('description', 'No description')}\n"
                    result += f"Dialogue: {panel.get('dialogue', 'No dialogue')}\n"
                    
                    # Check if image is available
                    image_filename = metadata_manager.get_image_filename(panel_number)
                    if image_filename:
                        result += f"Image: {image_filename}"
                    else:
                        result += "Image: Not generated yet"
                    
                    return result
                else:
                    return f"Panel {panel_number} not found."
            
            elif action == "get_images":
                image_filenames = metadata_manager.get_all_image_filenames()
                if image_filenames:
                    images_info = []
                    for panel_num, filename in image_filenames.items():
                        images_info.append(f"Panel {panel_num}: {filename}")
                    return "Generated Images:\n" + "\n".join(images_info)
                else:
                    return "No images generated yet."
            
            elif action == "get_summary":
                summary = metadata_manager.get_story_summary()
                result = f"Story Summary:\n"
                result += f"ID: {summary['story_id']}\n"
                result += f"Status: {summary['status']}\n"
                result += f"Topic: {summary['topic']}\n"
                result += f"Has Story Text: {summary['has_full_story']}\n"
                result += f"Panels: {summary['panel_count']}/6\n"
                result += f"Images: {summary['images_generated']}/6\n"
                result += f"Completed Agents: {', '.join(summary['completed_agents'])}\n"
                result += f"Last Updated: {summary['last_updated']}"
                return result
            
            elif action == "get_status":
                status = metadata_manager.get_story_status()
                completed_agents = metadata_manager.get_completed_agents()
                return f"Story Status: {status}\nCompleted Agents: {', '.join(completed_agents)}"
            
            else:
                return f"Unknown action: {action}. Available actions: get_topic, get_story_text, get_panels, get_panel, get_images, get_summary, get_status"
        
        except Exception as e:
            return f"Error reading story metadata: {str(e)}"


class StoryMetadataWriterTool(BaseTool):
    name: str = "StoryMetadataWriter"
    description: str = (
        "Write story information to the centralized story metadata file. "
        "Use this to save story content, panel descriptions, image filenames, and update generation status. "
        "Actions: 'set_topic', 'set_story_text', 'set_panels', 'set_image', 'mark_completed', 'set_status'"
    )
    args_schema: Type[BaseModel] = StoryMetadataWriteInput

    def _run(self, action: str, topic: Optional[str] = None, story_text: Optional[str] = None, 
            panels_json: Optional[str] = None, panel_number: Optional[int] = None,
            image_filename: Optional[str] = None, agent_name: Optional[str] = None,
            status: Optional[str] = None, details: Optional[str] = None) -> str:
        try:
            # Get or create story metadata manager
            metadata_manager = get_current_story_metadata()
            if not metadata_manager:
                # Create a new story metadata manager
                metadata_manager = StoryMetadataManager()
            
            if action == "set_topic":
                if not topic:
                    return "Topic is required for 'set_topic' action."
                metadata_manager.set_topic(topic)
                return f"Topic set to: {topic}"
            
            elif action == "set_story_text":
                if not story_text:
                    return "Story text is required for 'set_story_text' action."
                agent = agent_name or "unknown_agent"
                metadata_manager.set_full_story_text(story_text, agent)
                return f"Story text saved ({len(story_text)} characters) by {agent}"
            
            elif action == "set_panels":
                if not panels_json:
                    return "Panels JSON is required for 'set_panels' action."
                
                try:
                    panels_data = json.loads(panels_json)
                    if isinstance(panels_data, dict) and 'panels' in panels_data:
                        panels = panels_data['panels']
                    elif isinstance(panels_data, list):
                        panels = panels_data
                    else:
                        return "Invalid panels format. Expected list of panels or object with 'panels' key."
                    
                    agent = agent_name or "unknown_agent"
                    metadata_manager.set_panels(panels, agent)
                    return f"Panels saved ({len(panels)} panels) by {agent}"
                
                except json.JSONDecodeError as e:
                    return f"Invalid JSON format: {str(e)}"
            
            elif action == "set_image":
                if panel_number is None or not image_filename:
                    return "Both panel_number and image_filename are required for 'set_image' action."
                
                agent = agent_name or "unknown_agent"
                metadata_manager.set_image_filename(panel_number, image_filename, agent)
                return f"Image filename saved for Panel {panel_number}: {image_filename}"
            
            elif action == "mark_completed":
                if not agent_name:
                    return "Agent name is required for 'mark_completed' action."
                
                metadata_manager.mark_agent_completed(agent_name, details or "")
                return f"Agent {agent_name} marked as completed"
            
            elif action == "set_status":
                if not status:
                    return "Status is required for 'set_status' action."
                
                metadata_manager.set_story_status(status)
                return f"Story status set to: {status}"
            
            else:
                return f"Unknown action: {action}. Available actions: set_topic, set_story_text, set_panels, set_image, mark_completed, set_status"
        
        except Exception as e:
            return f"Error writing story metadata: {str(e)}"


class StoryMetadataLayoutTool(BaseTool):
    name: str = "StoryMetadataForLayout"
    description: str = (
        "Export story data from metadata file in format suitable for comic layout generation. "
        "Returns structured data with panels, dialogue, and image paths for ComicLayoutTool. "
        "Use this when you need to prepare data for final comic assembly."
    )
    args_schema: Type[BaseModel] = BaseModel

    def _run(self) -> str:
        try:
            metadata_manager = get_current_story_metadata()
            if not metadata_manager:
                return "No active story metadata found. Cannot export layout data."
            
            layout_data = metadata_manager.export_for_layout()
            
            # Return as JSON string for easy parsing by other tools
            return json.dumps(layout_data, indent=2)
        
        except Exception as e:
            return f"Error exporting layout data: {str(e)}"


# Create tool instances for easy importing
story_metadata_reader = StoryMetadataReaderTool()
story_metadata_writer = StoryMetadataWriterTool()  
story_metadata_layout = StoryMetadataLayoutTool()