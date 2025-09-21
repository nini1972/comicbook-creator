#!/usr/bin/env python3
"""
Quick verification of path fix results
"""
import os

def verify_path_fix():
    print("=== PATH FIX VERIFICATION ===")
    
    # Check if Gemini Image Tutorial path exists
    gemini_path = r"C:\Users\ninic\projects\Datacamp_projects\gemini-image-tutorial"
    print(f"1. Gemini Image Tutorial path: {gemini_path}")
    if os.path.exists(gemini_path):
        print("   ✅ FOUND")
        
        # Check output directory
        output_path = os.path.join(gemini_path, "output")
        if os.path.exists(output_path):
            print(f"2. Output directory: {output_path}")
            print("   ✅ FOUND")
            
            # Count files
            try:
                files = [f for f in os.listdir(output_path) if f.endswith('.png')]
                print(f"3. PNG files found: {len(files)}")
                if len(files) > 0:
                    print("   ✅ IMAGES AVAILABLE")
                    print("   First few files:")
                    for f in files[:3]:
                        print(f"     - {f}")
                else:
                    print("   ❌ NO PNG FILES")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
        else:
            print("   ❌ OUTPUT DIRECTORY NOT FOUND")
    else:
        print("   ❌ NOT FOUND")
    
    # Check if comic panels directory was created
    comic_panels_path = r"C:\Users\ninic\projects\CrewAI\comicbook\backend\output\comic_panels"
    print(f"4. Comic panels directory: {comic_panels_path}")
    if os.path.exists(comic_panels_path):
        print("   ✅ FOUND")
        try:
            files = os.listdir(comic_panels_path)
            print(f"   Files copied: {len(files)}")
            for f in files:
                size = os.path.getsize(os.path.join(comic_panels_path, f))
                print(f"     - {f} ({size:,} bytes)")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    else:
        print("   ❌ NOT CREATED YET")
    
    print("\n=== CONCLUSION ===")
    if os.path.exists(gemini_path) and os.path.exists(os.path.join(gemini_path, "output")):
        print("🎉 PATH FIX IS WORKING! Ready for full comic generation test.")
    else:
        print("❌ Path fix needs more work.")

if __name__ == "__main__":
    verify_path_fix()
