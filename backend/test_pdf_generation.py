"""
PDF Generation Comparison Test
Tests different approaches for converting Markdown comics to PDF with embedded images.
"""

import os
import sys
from pathlib import Path

# Add the backend src to path for imports
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

from src.utils.comic_exporter import ComicExporter


def test_current_weasyprint_approach():
    """Test the current WeasyPrint-based PDF generation"""
    print("=== Testing Current WeasyPrint Approach ===")
    
    # Sample markdown with actual panel images
    test_markdown = """# Test Comic Strip

![Panel 1](/comic_panels/panel_001_server_generated_gemini-image-tutorial_1759601043622.png)
Dialogue: NEXUS SYSTEM ALERT: CRITICAL ERROR DETECTED.

![Panel 2](/comic_panels/consistent_panel_002_maya chen_1759601060726.png)
Dialogue: Detective Chen, we have a problem.

![Panel 3](/comic_panels/multi_char_panel_003_maya_chen_aria_1759601143027.png)
Dialogue: ARIA: I'm detecting the virus source.
"""
    
    try:
        exporter = ComicExporter("test_weasyprint")
        markdown_path = exporter.save_markdown(test_markdown)
        pdf_path = exporter.generate_pdf(test_markdown)
        
        print(f"✅ WeasyPrint Success:")
        print(f"   Markdown: {markdown_path}")
        print(f"   PDF: {pdf_path}")
        
        # Check if PDF was actually created
        if Path(pdf_path).exists():
            print(f"   PDF file size: {Path(pdf_path).stat().st_size} bytes")
            return True
        else:
            print("   ❌ PDF file not found")
            return False
            
    except Exception as e:
        print(f"❌ WeasyPrint Error: {e}")
        return False


def test_markdown_pdf_approach():
    """Test the GitHub Copilot recommended markdown-pdf approach"""
    print("\n=== Testing Markdown-PDF Approach ===")
    
    try:
        from markdown_pdf import MarkdownPdf, Section
        
        # Create markdown content with backend file paths (as recommended)
        backend_panels_dir = Path("output/comic_panels")
        
        # Sample markdown with local file paths
        test_markdown = f"""# Test Comic Strip (markdown-pdf)

![Panel 1]({backend_panels_dir}/panel_001_server_generated_gemini-image-tutorial_1759601043622.png)
Dialogue: NEXUS SYSTEM ALERT: CRITICAL ERROR DETECTED.

![Panel 2]({backend_panels_dir}/consistent_panel_002_maya chen_1759601060726.png)
Dialogue: Detective Chen, we have a problem.

![Panel 3]({backend_panels_dir}/multi_char_panel_003_maya_chen_aria_1759601143027.png)
Dialogue: ARIA: I'm detecting the virus source.
"""
        
        # Generate PDF
        pdf = MarkdownPdf()
        pdf.add_section(Section(test_markdown))
        
        output_dir = Path("output/comic_exports")
        output_dir.mkdir(exist_ok=True)
        pdf_path = output_dir / "test_markdown_pdf.pdf"
        
        pdf.save(str(pdf_path))
        
        print(f"✅ Markdown-PDF Success:")
        print(f"   PDF: {pdf_path}")
        
        # Check if PDF was actually created
        if pdf_path.exists():
            print(f"   PDF file size: {pdf_path.stat().st_size} bytes")
            return True
        else:
            print("   ❌ PDF file not found")
            return False
            
    except ImportError:
        print("❌ markdown-pdf not installed")
        return False
    except Exception as e:
        print(f"❌ Markdown-PDF Error: {e}")
        return False


def check_image_paths():
    """Check which image paths actually exist"""
    print("\n=== Checking Image Path Accessibility ===")
    
    backend_dir = Path("output/comic_panels")
    frontend_dir = Path("../frontend/public/comic_panels")
    
    sample_files = [
        "panel_001_server_generated_gemini-image-tutorial_1759601043622.png",
        "consistent_panel_002_maya chen_1759601060726.png", 
        "multi_char_panel_003_maya_chen_aria_1759601143027.png"
    ]
    
    for filename in sample_files:
        backend_path = backend_dir / filename
        frontend_path = frontend_dir / filename
        
        print(f"\nFile: {filename}")
        print(f"  Backend ({backend_path}): {'✅ EXISTS' if backend_path.exists() else '❌ MISSING'}")
        print(f"  Frontend ({frontend_path}): {'✅ EXISTS' if frontend_path.exists() else '❌ MISSING'}")


def main():
    """Run all PDF generation tests"""
    print("Comic PDF Generation Test Suite")
    print("=" * 50)
    
    # Check image availability first
    check_image_paths()
    
    # Test current approach
    weasyprint_success = test_current_weasyprint_approach()
    
    # Test new approach
    markdown_pdf_success = test_markdown_pdf_approach()
    
    # Summary
    print("\n=== SUMMARY ===")
    print(f"WeasyPrint approach: {'✅ SUCCESS' if weasyprint_success else '❌ FAILED'}")
    print(f"Markdown-PDF approach: {'✅ SUCCESS' if markdown_pdf_success else '❌ FAILED'}")
    
    if weasyprint_success and markdown_pdf_success:
        print("\n🎉 Both approaches work! We can choose the best one.")
    elif weasyprint_success:
        print("\n⚠️ Only WeasyPrint works - may need to fix image paths for markdown-pdf")
    elif markdown_pdf_success:
        print("\n⚠️ Only Markdown-PDF works - should switch to this approach")
    else:
        print("\n❌ Both approaches failed - need to debug image path issues")


if __name__ == "__main__":
    main()