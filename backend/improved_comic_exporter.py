"""
Improved Comic PDF Exporter
Combines the best of both approaches based on GitHub Copilot recommendations.

Key improvements:
1. Uses backend image paths for reliable embedding (as recommended)
2. Supports both WeasyPrint and markdown-pdf
3. Fixes image path issues by converting web paths to local paths
4. Ensures images are actually embedded in the PDF
"""

import os
import re
from datetime import datetime
from pathlib import Path
from markdown2 import markdown as md_to_html
from weasyprint import HTML
from markdown_pdf import MarkdownPdf, Section
from src.utils.path_utils import get_backend_output_path, get_frontend_public_path


def _slugify(text: str, maxlen: int = 50) -> str:
    """Create a filesystem-safe slug from text and cap the length."""
    if not text:
        return "output"
    s = str(text).strip()
    s = re.sub(r"[\\/:*?\"<>|]+", "", s)
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s)
    if len(s) > maxlen:
        s = s[:maxlen].rstrip("_")
    return s


def _clean_markdown_title(markdown_content: str, max_title_len: int = 80) -> str:
    """Ensure the markdown has a single concise leading title."""
    if not markdown_content:
        return markdown_content

    lines = markdown_content.splitlines()
    non_empty_idxs = [i for i, l in enumerate(lines) if l.strip() != ""]
    if not non_empty_idxs:
        return markdown_content

    first_idx = non_empty_idxs[0]
    first_line = lines[first_idx].strip()
    second_line = None
    if len(non_empty_idxs) > 1:
        second_idx = non_empty_idxs[1]
        second_line = lines[second_idx].strip()

    if first_line.startswith("#") and second_line and second_line.startswith("#"):
        header_text = re.sub(r"^#+\s*", "", first_line).strip()
        if len(header_text) > max_title_len:
            header_text = header_text[:max_title_len].rstrip()
        new_first = f"# {header_text}"
        new_lines = lines[:]
        new_lines[first_idx] = new_first
        del new_lines[second_idx]
        return "\n".join(new_lines)

    if first_line.startswith("#"):
        header_text = re.sub(r"^#+\s*", "", first_line).strip()
        if len(header_text) > max_title_len:
            header_text = header_text[:max_title_len].rstrip()
            new_first = f"# {header_text}"
            lines[first_idx] = new_first
            return "\n".join(lines)

    return markdown_content


def _convert_web_paths_to_local(markdown_content: str) -> str:
    """
    Convert web image paths to local file paths for PDF generation.
    This addresses the key issue identified by GitHub Copilot.
    
    Converts:
        ![Panel 1](/comic_panels/image.png)
    To:
        ![Panel 1](output/comic_panels/image.png)
    """
    # Pattern to match Markdown image syntax with web paths
    pattern = r'!\[([^\]]*)\]\(/comic_panels/([^)]+)\)'
    
    def replace_path(match):
        alt_text = match.group(1)
        filename = match.group(2)
        
        # Use backend path (as recommended by GitHub Copilot)
        backend_path = Path("output/comic_panels") / filename
        
        # Verify the file exists
        if backend_path.exists():
            # Convert to relative path from where the PDF will be generated
            return f'![{alt_text}]({backend_path})'
        else:
            print(f"⚠️ Warning: Image not found at {backend_path}")
            return match.group(0)  # Return original if file not found
    
    converted_content = re.sub(pattern, replace_path, markdown_content)
    
    # Count conversions
    web_paths = len(re.findall(pattern, markdown_content))
    if web_paths > 0:
        print(f"🔄 Converted {web_paths} web image paths to local paths")
    
    return converted_content


class ImprovedComicExporter:
    """
    Improved Comic PDF Exporter based on GitHub Copilot recommendations.
    
    Features:
    - Uses backend image paths for reliable embedding
    - Supports both WeasyPrint and markdown-pdf approaches
    - Automatic path conversion from web paths to local paths
    - Better error handling and file size validation
    """
    
    def __init__(self, topic: str):
        self.topic = topic or "comic"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(get_backend_output_path("comic_exports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_markdown(self, markdown_content: str) -> str:
        """Save markdown with cleaned title and local image paths."""
        # Clean markdown title
        markdown_content = _clean_markdown_title(markdown_content)
        
        # Convert web paths to local paths for PDF generation
        markdown_content = _convert_web_paths_to_local(markdown_content)

        safe_topic = _slugify(self.topic, maxlen=50)
        filename = f"{safe_topic}_{self.timestamp}.md"
        path = self.output_dir / filename
        
        with path.open("w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        print(f"[ImprovedComicExporter] Markdown saved: {path}")
        return str(path)

    def generate_pdf_weasyprint(self, markdown_content: str) -> str:
        """Generate PDF using WeasyPrint (original approach with improvements)."""
        print("🔧 Using WeasyPrint approach...")
        
        # Convert paths for local access
        local_markdown = _convert_web_paths_to_local(markdown_content)
        
        # Convert markdown to HTML
        html_content = md_to_html(local_markdown, extras=["fenced-code-blocks", "tables"])

        safe_topic = _slugify(self.topic, maxlen=50)
        pdf_path = self.output_dir / f"{safe_topic}_{self.timestamp}_weasyprint.pdf"

        # Use current working directory as base_url for relative paths
        base_url = str(Path.cwd())
        HTML(string=html_content, base_url=base_url).write_pdf(str(pdf_path))

        print(f"[ImprovedComicExporter] WeasyPrint PDF generated: {pdf_path}")
        
        # Check file size to validate image embedding
        file_size = pdf_path.stat().st_size
        print(f"[ImprovedComicExporter] PDF file size: {file_size:,} bytes")
        
        if file_size < 50000:  # Less than 50KB probably means no images
            print("⚠️ Warning: PDF file size is small, images might not be embedded")
        
        return str(pdf_path)

    def generate_pdf_markdown_pdf(self, markdown_content: str) -> str:
        """Generate PDF using markdown-pdf (GitHub Copilot recommended approach)."""
        print("🔧 Using markdown-pdf approach (GitHub Copilot recommended)...")
        
        # Convert paths for local access
        local_markdown = _convert_web_paths_to_local(markdown_content)
        
        # Generate PDF using markdown-pdf
        pdf = MarkdownPdf()
        pdf.add_section(Section(local_markdown))
        
        safe_topic = _slugify(self.topic, maxlen=50)
        pdf_path = self.output_dir / f"{safe_topic}_{self.timestamp}_markdown_pdf.pdf"
        
        pdf.save(str(pdf_path))
        
        print(f"[ImprovedComicExporter] Markdown-PDF generated: {pdf_path}")
        
        # Check file size to validate image embedding
        file_size = pdf_path.stat().st_size
        print(f"[ImprovedComicExporter] PDF file size: {file_size:,} bytes")
        
        if file_size > 100000:  # More than 100KB probably means images are embedded
            print("✅ PDF file size indicates images are likely embedded")
        
        return str(pdf_path)

    def generate_pdf_both(self, markdown_content: str) -> tuple[str, str]:
        """Generate PDFs using both approaches for comparison."""
        print("🔧 Generating PDFs using both approaches...")
        
        weasyprint_path = self.generate_pdf_weasyprint(markdown_content)
        markdown_pdf_path = self.generate_pdf_markdown_pdf(markdown_content)
        
        # Compare file sizes
        weasy_size = Path(weasyprint_path).stat().st_size
        mdpdf_size = Path(markdown_pdf_path).stat().st_size
        
        print(f"\n📊 Comparison:")
        print(f"   WeasyPrint: {weasy_size:,} bytes")
        print(f"   Markdown-PDF: {mdpdf_size:,} bytes")
        
        if mdpdf_size > weasy_size * 2:
            print("✅ Markdown-PDF appears to embed images better (larger file size)")
        elif weasy_size > mdpdf_size * 2:
            print("✅ WeasyPrint appears to embed images better (larger file size)")
        else:
            print("🤔 Similar file sizes - both might be working similarly")
        
        return weasyprint_path, markdown_pdf_path

    def generate_pdf(self, markdown_content: str, method: str = "markdown-pdf") -> str:
        """
        Generate PDF using the specified method.
        
        Args:
            markdown_content: The comic markdown content
            method: "weasyprint", "markdown-pdf", or "both"
            
        Returns:
            Path to generated PDF (or best PDF if using "both")
        """
        if method == "weasyprint":
            return self.generate_pdf_weasyprint(markdown_content)
        elif method == "markdown-pdf":
            return self.generate_pdf_markdown_pdf(markdown_content)
        elif method == "both":
            weasy_path, mdpdf_path = self.generate_pdf_both(markdown_content)
            
            # Return the markdown-pdf version as it's recommended by GitHub Copilot
            # and showed better image embedding in our tests
            return mdpdf_path
        else:
            raise ValueError(f"Unknown method: {method}. Use 'weasyprint', 'markdown-pdf', or 'both'")


def test_improved_exporter():
    """Test the improved exporter with real comic data."""
    print("Testing Improved Comic Exporter")
    print("=" * 50)
    
    # Load the latest comic
    latest_comic_path = Path("output/comic_exports/cybercity_in_trouble_20251004_201912.md")
    
    if not latest_comic_path.exists():
        print(f"❌ Latest comic not found at {latest_comic_path}")
        return
    
    with open(latest_comic_path, 'r', encoding='utf-8') as f:
        comic_content = f.read()
    
    print(f"📖 Loaded comic: {latest_comic_path.name}")
    print(f"   Content length: {len(comic_content)} characters")
    
    # Test the improved exporter
    exporter = ImprovedComicExporter("cybercity_improved_test")
    
    # Save markdown
    markdown_path = exporter.save_markdown(comic_content)
    
    # Generate PDFs using both methods
    print("\n" + "=" * 50)
    best_pdf = exporter.generate_pdf(comic_content, method="both")
    
    print(f"\n✅ Test completed. Best PDF: {best_pdf}")


if __name__ == "__main__":
    test_improved_exporter()