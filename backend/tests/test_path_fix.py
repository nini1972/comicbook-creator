#!/usr/bin/env python3
"""
Quick test to verify that the Gemini Image Tutorial path is correctly resolved
"""
import os

def test_gemini_path():
    # This is the path we configured in gemini_image_tool.py
    gemini_tutorial_dir = r"C:\Users\ninic\projects\Datacamp_projects\gemini-image-tutorial"
    
    print(f"Testing Gemini Image Tutorial path: {gemini_tutorial_dir}")
    
    # Check if the directory exists
    if os.path.exists(gemini_tutorial_dir):
        print("✓ Gemini Image Tutorial directory found!")
        
        # Check for the output folder
        output_dir = os.path.join(gemini_tutorial_dir, "output")
        if os.path.exists(output_dir):
            print("✓ Output directory found!")
            
            # List files in output directory
            try:
                files = os.listdir(output_dir)
                print(f"Files in output directory: {len(files)} files")
                for file in files[:5]:  # Show first 5 files
                    print(f"  - {file}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more files")
            except Exception as e:
                print(f"Error listing output directory: {e}")
        else:
            print("✗ Output directory not found")
    else:
        print("✗ Gemini Image Tutorial directory not found")
    
    # Test a sample relative path resolution
    sample_relative_path = "output/server_generated_gemini-image-tutorial_1757861932330.png"
    resolved_path = os.path.join(gemini_tutorial_dir, sample_relative_path)
    print(f"\nSample path resolution:")
    print(f"Relative: {sample_relative_path}")
    print(f"Resolved: {resolved_path}")
    print(f"Exists: {os.path.exists(resolved_path)}")

if __name__ == "__main__":
    test_gemini_path()
