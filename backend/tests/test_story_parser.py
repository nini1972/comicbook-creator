import sys
import os
from pathlib import Path

# Add the src directory to the path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

# Change to the backend directory to handle relative imports
os.chdir(Path(__file__).parent.parent)

try:
    from visual_comic_crew.tools.story_parser_tool import StoryParserTool

    def test_story_parser():
        # Sample story text
        story_text = """
        Panel 1: A young hacker named Alex sits in a dimly lit room, surrounded by multiple computer screens. The screens display complex code and data visualizations. Alex wears glasses and has a focused expression. "I've finally found it," Alex says. "The breach in Cyberland's security system."
        
        Panel 2: Alex types rapidly on the keyboard, fingers dancing across the keys. The screens show a digital representation of Cyberland's network, with glowing nodes and connections. A notification pops up: "Intrusion Detected - Phantom Protocol Activated." Alex's eyes widen with concern. "This is bad," Alex mutters.
        
        Panel 3: The scene shifts to Cyberland's central hub, where digital avatars of the city's defenders materialize. Maya Chen, the lead security analyst, appears alarmed. "Phantom has breached our outer defenses," she announces to her team. "We need to act fast before it spreads."
        
        Panel 4: Maya and her team, including Alex Torres, work frantically to contain the breach. Holographic displays show the extent of the intrusion, with corrupted data streams spreading through the network. "I'm trying to isolate the affected sectors," Alex Torres says, sweat beading on his forehead.
        
        Panel 5: Maya Chen makes a critical decision. "We need to initiate the counterattack protocol," she declares. "Alex, can you trace Phantom's origin point?" Alex nods determinedly. "I'm already on it," he replies. "But we'll need to move quickly."
        
        Panel 6: In a dramatic final scene, Maya and Alex successfully neutralize Phantom, restoring Cyberland's security. The digital environment stabilizes, and the corrupted data streams disappear. "Cyberland is secure again," Maya announces with relief. "But we need to remain vigilant for future threats."
        """
        
        # Create the story parser tool
        parser = StoryParserTool()
        
        # Extract panels
        panels = parser._extract_panels(story_text)
        print("Extracted Panels:")
        for i, panel in enumerate(panels, 1):
            print(f"  Panel {i}: {panel}")
        
        # Extract dialogue
        dialogues = parser._extract_dialogue(story_text)
        print("\nExtracted Dialogue:")
        for i, dialogue in enumerate(dialogues, 1):
            print(f"  Panel {i}: {dialogue}")

    if __name__ == "__main__":
        test_story_parser()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this script from the backend directory")