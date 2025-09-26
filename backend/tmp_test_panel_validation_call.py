import os
import sys
# Ensure src is on PYTHONPATH
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from visual_comic_crew.tools.panel_validation_tool import PanelValidationTool

panel_map = {
    "1": "output\\comic_panels\\consistent_panel_001_hopebird_1758914202842.png",
    "2": [
        "output\\comic_panels\\consistent_panel_002_kind child_1758914286483.png",
        "output\\comic_panels\\consistent_panel_002_hopeful bird_1758914300504.png"
    ],
    "3": [
        "output\\comic_panels\\consistent_panel_003_kind child_1758914319409.png",
        "output\\comic_panels\\consistent_panel_003_hopeful bird_1758914330827.png"
    ],
    "4": "output\\comic_panels\\consistent_panel_004_hopeful bird_1758914349528.png",
    "5": "output\\comic_panels\\consistent_panel_005_kind child_1758914367711.png",
    "6": "server_generated_gemini-image-tutorial_1758914388518.png"
}

tool = PanelValidationTool()
result = tool._run(panel_map=panel_map, expected_panel_count=6)
print('\n=== TOOL RESULT START ===')
print(result)
print('=== TOOL RESULT END ===')
