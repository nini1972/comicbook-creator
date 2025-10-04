# not to use, is integrated in the comic_layout_tool.py 
# import sys
#import markdown2
#from weasyprint import HTML
#import os
#import sys

#def convert_md_to_pdf(md_path, pdf_path=None):
    if not os.path.isfile(md_path):
        print(f"Markdown file not found: {md_path}")
        return
    if pdf_path is None:
        pdf_path = os.path.splitext(md_path)[0] + ".pdf"

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_content = markdown2.markdown(md_content)
    css = """
    body { font-family: Arial, sans-serif; margin: 2em; }
    h1, h2, h3 { color: #333; }
    """
    html_full = f"<html><head><style>{css}</style></head><body>{html_content}</body></html>"

    # Set base_url to the markdown file's directory so image links resolve
    base_url = os.path.dirname(os.path.abspath(md_path))
    HTML(string=html_full, base_url=base_url).write_pdf(pdf_path)
    print(f"PDF saved to {pdf_path}")
    print(f"Markdown source retained at {md_path}")


#if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_md_to_pdf.py <markdown_file> [pdf_file]")
        sys.exit(1)
    md_path = sys.argv[1]
    pdf_path = sys.argv[2] if len(sys.argv) > 2 else None
    convert_md_to_pdf(md_path, pdf_path)
