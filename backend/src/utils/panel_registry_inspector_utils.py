from pathlib import Path
from typing import List, Tuple
from PIL import Image

def verify_image(path: Path) -> bool:
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False

def inspect_panel_registry(image_paths: List[str], dialogue: List[str]) -> Tuple[bool, List[str]]:
    """
    Verifies that all image paths exist and are readable.
    Returns a tuple: (is_valid, report_lines)
    """
    report = []
    valid = True

    if len(image_paths) != len(dialogue):
        report.append(f"❌ Mismatch: {len(image_paths)} images vs {len(dialogue)} dialogue lines")
        valid = False

    for i, path_str in enumerate(image_paths):
        path = Path(path_str)
        panel_num = i + 1

        if not path.exists():
            report.append(f"❌ Panel {panel_num}: Missing file → {path}")
            valid = False
        elif not verify_image(path):
            report.append(f"❌ Panel {panel_num}: Unreadable image → {path}")
            valid = False
        else:
            report.append(f"✅ Panel {panel_num}: OK → {path.name}")

    return valid, report