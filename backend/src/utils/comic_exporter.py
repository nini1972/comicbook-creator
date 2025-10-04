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
    # Normalize whitespace
    s = str(text).strip()
    # Remove characters that are unsafe for filenames
    s = re.sub(r"[\\/:*?\"<>|]+", "", s)
    # Replace non-alphanumeric with underscores
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    # Collapse multiple underscores
    s = re.sub(r"_+", "_", s)
    # Trim
    if len(s) > maxlen:
        s = s[:maxlen].rstrip("_")
    return s


def _clean_markdown_title(markdown_content: str, max_title_len: int = 80) -> str:
    """Ensure the markdown has a single concise leading title (one header line).

    If the first two non-empty lines are both headers, remove the second.
    Also truncate the title to a reasonable length to avoid excessively long filenames/titles.
    """
    if not markdown_content:
        return markdown_content

    lines = markdown_content.splitlines()
    # Find first two non-empty lines
    non_empty_idxs = [i for i, l in enumerate(lines) if l.strip() != ""]
    if not non_empty_idxs:
        return markdown_content

    first_idx = non_empty_idxs[0]
    first_line = lines[first_idx].strip()
    second_line = None
    if len(non_empty_idxs) > 1:
        second_idx = non_empty_idxs[1]
        second_line = lines[second_idx].strip()

    # If both are headers (start with '#'), keep only the first header and drop the second
    if first_line.startswith("#") and second_line and second_line.startswith("#"):
        # Truncate first header text
        header_text = re.sub(r"^#+\s*", "", first_line).strip()
        if len(header_text) > max_title_len:
            header_text = header_text[:max_title_len].rstrip()
        new_first = f"# {header_text}"
        # Rebuild content: replace first line, remove second header line
        new_lines = lines[:]
        new_lines[first_idx] = new_first
        # remove the second header line
        del new_lines[second_idx]
        return "\n".join(new_lines)

    # Otherwise, just truncate the first header if present
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


class ComicExporter:
    def __init__(self, topic: str):
        self.topic = topic or "comic"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Ensure output_dir is a Path
        self.output_dir = Path(get_backend_output_path("comic_exports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_markdown(self, markdown_content: str) -> str:
        # Clean markdown title to avoid duplicate headers
        markdown_content = _clean_markdown_title(markdown_content)
        
        # Convert web paths to local paths for PDF generation (GitHub Copilot recommendation)
        markdown_content = _convert_web_paths_to_local(markdown_content)

        safe_topic = _slugify(self.topic, maxlen=50)
        filename = f"{safe_topic}_{self.timestamp}.md"
        path = self.output_dir / filename
        with path.open("w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"[ComicExporter] Markdown saved: {path}")
        return str(path)

    def generate_pdf(self, markdown_content: str, method: str = "markdown-pdf") -> str:
        """
        Generate PDF using the specified method.
        
        Args:
            markdown_content: The comic markdown content
            method: "weasyprint" or "markdown-pdf" (recommended by GitHub Copilot)
            
        Returns:
            Path to generated PDF
        """
        if method == "markdown-pdf":
            return self._generate_pdf_markdown_pdf(markdown_content)
        elif method == "weasyprint":
            return self._generate_pdf_weasyprint(markdown_content)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'weasyprint' or 'markdown-pdf'")
    
    def _generate_pdf_weasyprint(self, markdown_content: str) -> str:
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

        print(f"[ComicExporter] WeasyPrint PDF generated: {pdf_path}")
        
        # Check file size to validate image embedding
        file_size = pdf_path.stat().st_size
        print(f"[ComicExporter] PDF file size: {file_size:,} bytes")
        
        return str(pdf_path)
    
    def _generate_pdf_markdown_pdf(self, markdown_content: str) -> str:
        """Generate PDF using markdown-pdf (GitHub Copilot recommended approach)."""
        print("🔧 Using markdown-pdf approach (GitHub Copilot recommended)...")
        
        # Convert paths for local access
        local_markdown = _convert_web_paths_to_local(markdown_content)
        
        # Generate PDF using markdown-pdf
        pdf = MarkdownPdf()
        pdf.add_section(Section(local_markdown))
        
        safe_topic = _slugify(self.topic, maxlen=50)
        pdf_path = self.output_dir / f"{safe_topic}_{self.timestamp}.pdf"
        
        pdf.save(str(pdf_path))
        
        print(f"[ComicExporter] Markdown-PDF generated: {pdf_path}")
        
        # Check file size to validate image embedding
        file_size = pdf_path.stat().st_size
        print(f"[ComicExporter] PDF file size: {file_size:,} bytes")
        
        if file_size > 100000:  # More than 100KB probably means images are embedded
            print("✅ PDF file size indicates images are likely embedded")
        
        return str(pdf_path)