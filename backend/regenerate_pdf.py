#!/usr/bin/env python3
"""
Script to regenerate the PDF file with the updated markdown content.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Now we can import from the updated comic_exporter
from src.utils.comic_exporter import ComicExporter

def regenerate_pdf():
    """Regenerate the PDF file with updated markdown content."""
    # Define paths
    md_path = Path("backend/output/comic_exports/the town hero under attack_20251002_233309.md")
    pdf_path = Path("backend/output/comic_exports/the town hero under attack_20251002_233309_updated.pdf")
    
    # Check if markdown file exists
    if not md_path.exists():
        print(f"❌ Markdown file not found: {md_path}")
        return
    
    # Read markdown content
    with open(md_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    # Use the ComicExporter to generate PDF
    # We'll create a temporary exporter with a dummy topic
    exporter = ComicExporter("the town hero under attack")
    
    # Create PDF with images
    # Use the backend root directory as base_url to properly resolve relative image paths
    base_url = str(backend_path.resolve())
    print(f"Using base URL: {base_url}")
    
    # Since we can't directly access the private method, we'll recreate the logic
    from markdown2 import markdown as md_to_html
    from weasyprint import HTML
    
    html_content = md_to_html(markdown_content, extras=["fenced-code-blocks", "tables"])
    HTML(string=html_content, base_url=base_url).write_pdf(pdf_path)
    
    print(f"✅ PDF regenerated: {pdf_path}")
    print("✅ Images should now be visible in the PDF")

def main():
    """Main function."""
    print("🔧 Regenerating PDF with updated markdown")
    print("=" * 40)
    
    regenerate_pdf()
    
    print("\n✅ Process completed!")

if __name__ == "__main__":
    main()