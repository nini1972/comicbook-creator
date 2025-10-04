"""
Panel Filename Validation and Repair Utility
Helps ensure consistent filename formatting across all image generation tools.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from src.utils.path_utils import get_backend_output_path


def validate_panel_filename(filename: str) -> bool:
    """
    Validate that a panel filename follows the expected naming convention.
    
    Expected patterns:
    - consistent_panel_001_character_name_timestamp.png
    - multi_char_panel_001_char1_char2_timestamp.png
    - server_generated_gemini-image-tutorial_timestamp.png
    
    Args:
        filename: The filename to validate
        
    Returns:
        bool: True if filename follows naming convention, False otherwise
    """
    # Remove .png extension for pattern matching
    name_without_ext = filename.replace('.png', '')
    
    # Define valid patterns
    patterns = [
        r'^consistent_panel_\d{3}_[a-z_]+_\d+$',  # consistent panel format
        r'^multi_char_panel_\d{3}_[a-z_]+_\d+$',  # multi-character format
        r'^server_generated_gemini-image-tutorial_\d+$',  # gemini format
        r'^panel_\d{3}_server_generated_gemini-image-tutorial_\d+$'  # alternate gemini format
    ]
    
    for pattern in patterns:
        if re.match(pattern, name_without_ext):
            return True
    
    return False


def normalize_character_name_for_filename(character_name: str) -> str:
    """
    Normalize a character name for use in filenames.
    
    Args:
        character_name: Original character name
        
    Returns:
        str: Normalized name suitable for filenames
    """
    return character_name.lower().replace(' ', '_').replace('-', '_')


def fix_panel_filename(original_filename: str) -> str:
    """
    Fix a panel filename to ensure proper formatting.
    
    Args:
        original_filename: The original filename
        
    Returns:
        str: Fixed filename with proper formatting
    """
    # If already valid, return as-is
    if validate_panel_filename(original_filename):
        return original_filename
    
    # Try to fix common issues
    fixed_filename = original_filename
    
    # Replace spaces with underscores
    fixed_filename = fixed_filename.replace(' ', '_')
    
    # Replace multiple underscores with single underscore
    fixed_filename = re.sub(r'_+', '_', fixed_filename)
    
    # Ensure lowercase except for file extension
    name_part, ext = os.path.splitext(fixed_filename)
    fixed_filename = name_part.lower() + ext
    
    return fixed_filename


def scan_panel_directory() -> Dict[str, List[str]]:
    """
    Scan the comic panels directory and categorize files by naming convention.
    
    Returns:
        Dict with 'valid', 'invalid', and 'missing_underscore' lists
    """
    panels_dir = get_backend_output_path("comic_panels")
    
    result = {
        'valid': [],
        'invalid': [],
        'missing_underscore': []
    }
    
    if not os.path.exists(panels_dir):
        return result
    
    for filename in os.listdir(panels_dir):
        if not filename.endswith('.png'):
            continue
            
        if validate_panel_filename(filename):
            result['valid'].append(filename)
        else:
            result['invalid'].append(filename)
            
            # Check if it's a spacing issue
            fixed_name = fix_panel_filename(filename)
            if validate_panel_filename(fixed_name) and fixed_name != filename:
                result['missing_underscore'].append(filename)
    
    return result


def repair_panel_filenames(dry_run: bool = True) -> List[Tuple[str, str]]:
    """
    Repair invalid panel filenames in the comic panels directory.
    
    Args:
        dry_run: If True, only show what would be renamed without actually doing it
        
    Returns:
        List of (old_filename, new_filename) tuples that were/would be renamed
    """
    panels_dir = get_backend_output_path("comic_panels")
    renamed_files = []
    
    if not os.path.exists(panels_dir):
        print(f"Panels directory not found: {panels_dir}")
        return renamed_files
    
    scan_results = scan_panel_directory()
    
    for invalid_filename in scan_results['invalid']:
        fixed_filename = fix_panel_filename(invalid_filename)
        
        if fixed_filename != invalid_filename and validate_panel_filename(fixed_filename):
            old_path = os.path.join(panels_dir, invalid_filename)
            new_path = os.path.join(panels_dir, fixed_filename)
            
            if dry_run:
                print(f"Would rename: {invalid_filename} -> {fixed_filename}")
                renamed_files.append((invalid_filename, fixed_filename))
            else:
                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed: {invalid_filename} -> {fixed_filename}")
                    renamed_files.append((invalid_filename, fixed_filename))
                except Exception as e:
                    print(f"Error renaming {invalid_filename}: {e}")
    
    return renamed_files


def print_panel_directory_report():
    """Print a detailed report of the panel directory status."""
    scan_results = scan_panel_directory()
    
    print("=== Panel Directory Report ===")
    print(f"Valid filenames: {len(scan_results['valid'])}")
    print(f"Invalid filenames: {len(scan_results['invalid'])}")
    print(f"Missing underscores: {len(scan_results['missing_underscore'])}")
    print()
    
    if scan_results['valid']:
        print("✅ Valid files:")
        for filename in sorted(scan_results['valid']):
            print(f"  {filename}")
        print()
    
    if scan_results['invalid']:
        print("❌ Invalid files:")
        for filename in sorted(scan_results['invalid']):
            fixed = fix_panel_filename(filename)
            print(f"  {filename} -> {fixed}")
        print()
    
    if scan_results['missing_underscore']:
        print("⚠️ Files with spacing issues:")
        for filename in sorted(scan_results['missing_underscore']):
            print(f"  {filename}")
        print()


if __name__ == "__main__":
    print_panel_directory_report()
    print("\nTo fix filenames, run:")
    print("repair_panel_filenames(dry_run=False)")