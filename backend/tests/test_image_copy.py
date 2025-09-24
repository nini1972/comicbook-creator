#!/usr/bin/env python3
"""
Test the gemini_image_tool path fix without importing CrewAI
"""
import os
import shutil
import tempfile

# Simulate the path resolution logic from gemini_image_tool.py
def test_image_copy():
    # Simulate response from Gemini Image Tutorial server
    response_data = {
        "status": "success",
        "image_path": "output/server_generated_gemini-image-tutorial_17.png"  # One of the files we saw
    }
    
    source_image_path = response_data["image_path"]
    print(f"Original relative path: {source_image_path}")
    
    # Apply the same logic as in gemini_image_tool.py
    if not os.path.isabs(source_image_path):
        # Gemini Image Tutorial is located at C:\Users\ninic\projects\Datacamp_projects\gemini-image-tutorial
        gemini_tutorial_dir = r"C:\Users\ninic\projects\Datacamp_projects\gemini-image-tutorial"
        source_image_path = os.path.join(gemini_tutorial_dir, source_image_path)
    
    print(f"Resolved source path: {source_image_path}")
    
    # Check if source file exists
    if not os.path.exists(source_image_path):
        print(f"❌ Source file not found: {source_image_path}")
        return False
    
    print(f"✅ Source file found: {source_image_path}")
    
    # Extract filename from the source path
    source_filename = os.path.basename(source_image_path)
    print(f"Source filename: {source_filename}")
    
    # Define destination directory (comic_panels folder)
    output_dir = os.path.join(os.getcwd(), "output", "comic_panels")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Copy the image to our output directory
    destination_path = os.path.join(output_dir, source_filename)
    
    try:
        # Copy the file from Gemini Image Tutorial to our comic project
        shutil.copy2(source_image_path, destination_path)
        print(f"✅ Image copied successfully to: {destination_path}")
        
        # Check if the copied file exists
        if os.path.exists(destination_path):
            file_size = os.path.getsize(destination_path)
            print(f"✅ Copied file verified. Size: {file_size} bytes")
            
            # Return the relative path that can be used in markdown
            relative_path = f"images/comic_panels/{source_filename}"
            print(f"✅ Markdown relative path: {relative_path}")
            return True
        else:
            print(f"❌ Copied file not found at destination")
            return False
            
    except Exception as copy_error:
        print(f"❌ Failed to copy image: {copy_error}")
        return False

if __name__ == "__main__":
    print("Testing image copy functionality...")
    success = test_image_copy()
    if success:
        print("\n🎉 Path fix is working correctly!")
    else:
        print("\n❌ Path fix needs more work.")
