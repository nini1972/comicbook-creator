from crewai.tools import BaseTool
import requests
from typing import Type, Optional, List
from pydantic import BaseModel, Field

class GeminiImageToolSchema(BaseModel):
    """Input for GeminiImageTool."""
    prompt: str = Field(..., description="The detailed prompt for image generation.")
    base_image_paths: Optional[List[str]] = Field(None, description="Optional list of local file paths for base images to be used as reference.")

class GeminiImageTool(BaseTool):
    name: str = "Gemini Image Generator"
    description: str = "Generates an image using a local MCP server with Gemini Flash 2.5. Use this to create visuals based on a prompt."
    args_schema: Type[BaseModel] = GeminiImageToolSchema
    server_url: str = "http://127.0.0.1:8000/generate-image/"

    def _run(
        self,
        prompt: str,
        base_image_paths: Optional[List[str]] = None,
    ) -> str:
        """Use the tool."""
        payload = {"prompt": prompt}
        if base_image_paths:
            payload["base_image_paths"] = base_image_paths
        
        try:
            response = requests.post(self.server_url, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            response_data = response.json()
            
            if response_data.get("status") == "success" and response_data.get("image_path"):
                image_path = response_data["image_path"]
                return f"Image generated successfully. Saved at: {image_path}"
            else:
                # Try to get a meaningful error message from the server's response
                error_message = response_data.get("message") or response_data.get("detail") or "Unknown error from image generation server."
                return f"Error: {error_message}"

        except requests.exceptions.RequestException as e:
            return f"Error connecting to the image generation server: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

