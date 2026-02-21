from PIL import Image
import os
from pathlib import Path

def generate_web_icons(source_image_path, output_dir="output/icons"):
    """
    Generates various web icon sizes and formats from a source image.
    
    Args:
        source_image_path (str): Path to the source image (preferably large and square).
        output_dir (str): Directory where the icons will be saved.
    """
    try:
        source = Image.open(source_image_path)
        
        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Convert to RGBA if not already (for transparency support)
        if source.mode != 'RGBA':
            source = source.convert('RGBA')
            
        print(f"🚀 Generating icons in {output_path}...")
        
        # 1. favicon.ico (Multiple sizes: 16, 32, 48)
        # Pillow handles multi-resolution ICOs automatically
        ico_sizes = [(16, 16), (32, 32), (48, 48)]
        source.save(output_path / "favicon.ico", format="ICO", sizes=ico_sizes)
        print("✅ Created favicon.ico")
        
        # 2. favicon.png (512x512)
        favicon_512 = source.resize((512, 512), Image.Resampling.LANCZOS)
        favicon_512.save(output_path / "favicon.png", "PNG")
        print("✅ Created favicon.png (512x512)")
        
        # 3. icon-192.png (Android)
        icon_192 = source.resize((192, 192), Image.Resampling.LANCZOS)
        icon_192.save(output_path / "icon-192.png", "PNG")
        print("✅ Created icon-192.png")
        
        # 4. icon-512.png (PWA)
        icon_512 = source.resize((512, 512), Image.Resampling.LANCZOS)
        icon_512.save(output_path / "icon-512.png", "PNG")
        print("✅ Created icon-512.png")
        
        # 5. apple-touch-icon.png (iOS - 180x180)
        apple_icon = source.resize((180, 180), Image.Resampling.LANCZOS)
        apple_icon.save(output_path / "apple-touch-icon.png", "PNG")
        print("✅ Created apple-touch-icon.png")
        
        return True
    except Exception as e:
        print(f"❌ Error generating icons: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        generate_web_icons(sys.argv[1])
    else:
        print("Usage: python favicon_generator.py <path_to_source_image>")
