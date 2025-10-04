import re
from typing import List

def extract_panels(story_text: str) -> List[str]:
    """Extract panel descriptions from the story text."""
    # Look for patterns like "Panel 1:", "Panel 1)", "1.", etc.
    panel_pattern = r'(?:Panel\s*(\d+)[\:\)\.]|(\d+)\.)\s*(.*?)(?=\n(?:Panel\s*\d+[\:\)\.]|\d+\.|\n|$))'
    panels = []
    
    # Try to find panel descriptions
    matches = re.findall(panel_pattern, story_text, re.DOTALL | re.IGNORECASE)
    if matches:
        for match in matches:
            if match[0]:  # Panel X: format
                panels.append(match[2].strip())
            elif match[1]:  # X. format
                panels.append(match[2].strip())
    else:
        # If no clear panel markers, try to split the story into 6 parts
        # This is a fallback approach
        sentences = re.split(r'[.!?]+', story_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) >= 6:
            # Distribute sentences across 6 panels
            sentences_per_panel = len(sentences) // 6
            for i in range(6):
                start = i * sentences_per_panel
                end = start + sentences_per_panel if i < 5 else len(sentences)
                panel_text = '. '.join(sentences[start:end]) + '.'
                panels.append(panel_text)
        else:
            # If we can't split properly, return the whole story as one panel
            panels = [story_text]
            
    # Ensure we have exactly 6 panels
    while len(panels) < 6:
        panels.append("")
    return panels[:6]

def extract_dialogue(story_text: str) -> List[str]:
    """Extract dialogue from the story text."""
    # Look for dialogue patterns in quotes
    dialogue_pattern = r'["\u201c\u201d](.*?)[ "\u201c\u201d]'
    dialogues = re.findall(dialogue_pattern, story_text, re.DOTALL)
    
    # If no dialogue found, create empty dialogue for each panel
    if not dialogues:
        dialogues = [""] * 6
    else:
        # Ensure we have exactly 6 dialogue entries
        while len(dialogues) < 6:
            dialogues.append("")
        dialogues = dialogues[:6]
        
    return dialogues

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
    
    # Extract panels
    panels = extract_panels(story_text)
    print("Extracted Panels:")
    for i, panel in enumerate(panels, 1):
        print(f"  Panel {i}: {panel}")
    
    # Extract dialogue
    dialogues = extract_dialogue(story_text)
    print("\nExtracted Dialogue:")
    for i, dialogue in enumerate(dialogues, 1):
        print(f"  Panel {i}: {dialogue}")

if __name__ == "__main__":
    test_story_parser()