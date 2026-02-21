"""
Quick test to verify image save operations work correctly.
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image  
from src.utils.path_utils import get_backend_output_path

def test_basic_save():
    """Test basic PIL image save to backend folder."""
    print("\n=== Test 1: Basic PIL Save ===")
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='blue')
    
    # Save to backend
    output_dir = get_backend_output_path("comic_panels")
    os.makedirs(output_dir, exist_ok=True)
    dest_path = output_dir / "test_basic_save.png"
    
    print(f"Saving to: {dest_path}")
    img.save(dest_path)
    
    # Verify
    if os.path.exists(dest_path):
        size = os.path.getsize(dest_path)
        print(f"✅ File exists: {size} bytes")
        # Cleanup
        os.remove(dest_path)
        return True
    else:
        print(f"❌ File not found after save")
        return False

def test_generate_image():
    """Test using the actual generate_image function."""
    print("\n=== Test 2: Generate Image via Core Function ===")
    
    from src.image_generator.core import generate_image
    
    prompt = "A simple test image of a blue square"
    print(f"Generating image with prompt: {prompt}")
    
    result = generate_image(prompt)
    
    if result:
        print(f"✅ Image generated successfully")
        
        # Try to save it
        output_dir = get_backend_output_path("comic_panels")
        dest_path = output_dir / "test_generated.png"
        
        try:
            result.save(dest_path)
            if os.path.exists(dest_path):
                size = os.path.getsize(dest_path)
                print(f"✅ Saved generated image: {size} bytes")
                os.remove(dest_path)
                return True
            else:
                print(f"❌ Generated image not saved")
                return False
        except Exception as e:
            print(f"❌ Error saving: {e}")
            return False
    else:
        print(f"❌ Image generation failed")
        return False

if __name__ == "__main__":
    print("Testing image save operations...")
    
    test1 = test_basic_save()
    print(f"\nTest 1 result: {'PASS' if test1 else 'FAIL'}")
    
    test2 = test_generate_image()
    print(f"Test 2 result: {'PASS' if test2 else 'FAIL'}")
    
    print(f"\n{'=' * 50}")
    if test1 and test2:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
