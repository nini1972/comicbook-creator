import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from pathlib import Path

# Load your API key from the .env file
load_dotenv()

# Create a client to talk to Gemini
api_key = os.getenv("GOOGLE_GENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)


def check_video_model_access():
    """
    Checks if the current API key has access to video generation models.
    
    Returns:
        str: The name of the available video model, or None.
    """
    try:
        print("🔍 Checking video model access...")
        video_models = []
        for model in client.models.list():
            if 'veo' in model.name.lower():
                video_models.append(model.name)
        
        if video_models:
            # Prefer veo-2-001 if available
            best_model = next((m for m in video_models if "veo-2-001" in m), video_models[0])
            print(f"✅ Video model access confirmed: {best_model}")
            return best_model
        else:
            print("⚠️ No direct 'veo' models found. Checking for 'imagen' video models...")
            imagen_models = []
            for model in client.models.list():
                if 'imagen' in model.name.lower() and 'video' in model.name.lower():
                    imagen_models.append(model.name)
            
            if imagen_models:
                print(f"✅ Video model access confirmed: {imagen_models[0]}")
                return imagen_models[0]
            
    except Exception as e:
        print(f"❌ Could not list models: {e}")
    
    print("❌ No video generation models found with your current credentials.")
    return None


def generate_video(prompt, base_image_path, model_name="veo-2-001"):
    """
    Generates a 5-second video from a prompt and a base image.

    Args:
        prompt (str): Description of the motion/scene.
        base_image_path (str): Path to the source image.
        model_name (str): The video model to use.

    Returns:
        bytes: The video data as bytes, or None.
    """
    try:
        print(f"🎬 Initializing video generation with model: {model_name}...")
        
        # Open image for the SDK - use keyword argument 'location'
        source_image = types.Image.from_file(location=base_image_path)
        
        # Start the long-running operation
        operation = client.models.generate_videos(
            model=model_name,
            prompt=prompt,
            image=source_image,
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                duration_seconds=5,
                enhance_prompt=True,
            )
        )

        print("⏳ Generation started. Polling for results...")
        
        # Polling loop
        while not operation.done:
            time.sleep(5)
            operation = client.operations.get(operation)
        
        if operation.response and operation.response.generated_videos:
            # For Veo/Imagen models, we typically download the result
            video_obj = operation.response.generated_videos[0].video
            # Note: Depending on the specific SDK version return, we might need to download
            # Here we assume the operation returns the file object which we can then download
            return video_obj
            
    except Exception as e:
        print(f"❌ Error during video generation: {e}")
    
    return None


def generate_image(prompt, base_images=None):
    """
    Generates an image from a prompt, optionally using one or more base images.

    Args:
        prompt (str): The text prompt.
        base_images (list[PIL.Image.Image], optional): A list of base images for refinement or composition. Defaults to None.

    Returns:
        PIL.Image.Image: The generated image object, or None.
    """
    try:
        contents = [prompt]
        if base_images:
            contents.extend(base_images)

        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=contents
        )

        # --- Start of robust response handling ---
        if not response.candidates:
            print("❌ The model did not return any candidates. This might be due to a safety block.")
            # Try to print more details if available
            try:
                print(f"Prompt Feedback: {response.prompt_feedback}")
            except Exception:
                pass # Ignore if prompt_feedback is not available
            return None

        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            print("❌ The model's response was empty. This can happen if the prompt is blocked for safety reasons.")
            print(f"Finish Reason: {candidate.finish_reason}")
            print(f"Safety Ratings: {candidate.safety_ratings}")
            return None
        # --- End of robust response handling ---

        for part in candidate.content.parts:
            if part.inline_data is not None:
                return Image.open(BytesIO(part.inline_data.data))

    except Exception as e:
        print(f"❌ Error during image generation: {e}")
    
    return None


def generate_and_save_image(prompt, filename):
   """
   Generate an image and save it to the output folder
  
   Args:
       prompt (str): Description of what you want to create
       filename (str): Name for the saved image file
  
   Returns:
       bool: True if successful, False otherwise
   """
   image = generate_image(prompt)
   if image:
       try:
           # Ensure output directory exists
           output_dir = Path("output")
           output_dir.mkdir(exist_ok=True)
           
           image_path = output_dir / filename
           image.save(image_path)
           print(f"✅ Image saved as {image_path}")
           return True
       except Exception as e:
           print(f"❌ Error saving image: {e}")
   return False
