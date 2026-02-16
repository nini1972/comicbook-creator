"""
Dedicated Speech Bubble Tool for Comic Panels
A specialized tool focused exclusively on adding speech bubbles and dialogue to comic panels.
"""

import os
from pathlib import Path
from typing import Optional, Type, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests
import time
import json
from src.utils.registry_utils import update_registry_entry
from src.utils.image_utils import (
    resolve_image_path,
    retry_file_check,
    verify_image_readable,
    copy_image_to_output,
    update_registry_for_image,
    prepare_temp_images_for_gemini
)


class SpeechBubbleToolSchema(BaseModel):
    """Input schema for Speech Bubble Tool."""
    panel_image_path: str = Field(..., description="Path to the comic panel image")
    dialogue_text: str = Field(..., description="Text to include in the speech bubble")
    bubble_style: str = Field("classic", description="Style: 'classic', 'thought', 'shout', 'whisper', 'narration'")
    character_position: str = Field("auto", description="Character position: 'left', 'right', 'center', 'auto'")
    panel_number: int = Field(1, description="Panel number for organization")
    # Advanced options
    text_size: str = Field("medium", description="Text size: 'small', 'medium', 'large'")
    bubble_color: str = Field("auto", description="Bubble color: 'auto', 'white', 'yellow', 'blue', 'pink', 'green', 'transparent', 'semi-transparent'")
    transparency: float = Field(1.0, description="Transparency level: 0.0 (fully transparent) to 1.0 (fully opaque)")
    color_intensity: str = Field("medium", description="Color intensity: 'light', 'medium', 'dark'")
    auto_enhance: bool = Field(True, description="Enable automatic color and style enhancement based on dialogue analysis")
    multiple_bubbles: bool = Field(False, description="Whether dialogue should be split into multiple bubbles")


class SpeechBubbleTool(BaseTool):
    """
    Specialized tool for adding professional speech bubbles to comic panels.
    
    Features:
    - Multiple bubble styles (classic, thought, shout, whisper, narration)
    - Smart positioning to avoid covering important elements
    - Professional comic book text formatting
    - Support for multiple bubbles per panel
    - Customizable styling options
    """
    
    name: str = "Speech Bubble Tool"
    description: str = (
        "Adds professional comic book speech bubbles with dialogue text to existing comic panels. "
        "Supports various bubble styles (classic white bubbles, thought clouds, shout bubbles, etc.) "
        "with intelligent positioning and comic-book quality text formatting. Essential for creating "
        "comics with integrated dialogue instead of separate text below panels."
    )
    args_schema: Type[BaseModel] = SpeechBubbleToolSchema
    server_url: str = os.getenv("GEMINI_IMAGE_SERVER_URL", "http://127.0.0.1:8000/generate-image/")

    def __init__(self):
        super().__init__()

    def _analyze_dialogue_emotion(self, dialogue: str) -> dict:
        """Analyze dialogue text to determine emotional context and appropriate styling."""
        dialogue_lower = dialogue.lower()
        
        emotion_analysis = {
            "emotion": "neutral",
            "intensity": "medium",
            "suggested_color": "white",
            "suggested_transparency": 1.0,
            "suggested_effects": []
        }
        
        # Check for specific emotions with priority order (most specific first)
        
        # Excitement/Happy - check early to avoid conflict with sarcasm
        if ("!" in dialogue and 
              any(word in dialogue_lower for word in ["wow", "amazing", "great", "awesome", "fantastic", "wonderful", "incredible"]) and
              not any(phrase in dialogue_lower for phrase in ["oh great", "just great"])):
            emotion_analysis["emotion"] = "excited"
            emotion_analysis["intensity"] = "high"
            emotion_analysis["suggested_color"] = "yellow"
            emotion_analysis["suggested_effects"] = ["glow"]
            
        # Inner thoughts/Self-talk - often in parentheses or with specific patterns (but not guilt patterns)
        elif (dialogue.startswith("(") and dialogue.endswith(")")) or \
           (any(phrase in dialogue_lower for phrase in ["i think", "i wonder", "maybe i", "what if"]) and
            not any(phrase in dialogue_lower for phrase in ["shouldn't have", "my fault"])):
            emotion_analysis["emotion"] = "inner_thought"
            emotion_analysis["suggested_color"] = "light_gray"
            emotion_analysis["suggested_transparency"] = 0.7
            emotion_analysis["suggested_effects"] = ["italic_style", "soft_border"]
            
        # Sarcasm/Irony - often has quotes or specific patterns (avoid excited conflicts)
        elif (any(phrase in dialogue_lower for phrase in ["oh great", "wonderful", "just perfect", "how lovely"]) and
              not any(word in dialogue_lower for word in ["amazing", "incredible"])) or \
             (dialogue.count('"') >= 2):
            emotion_analysis["emotion"] = "sarcastic"
            emotion_analysis["suggested_color"] = "dark_green"
            emotion_analysis["suggested_transparency"] = 0.9
            emotion_analysis["suggested_effects"] = ["tilted", "air_quotes"]
            
        # Nostalgia/Memory - reminiscing about the past
        elif any(phrase in dialogue_lower for phrase in ["i remember", "back then", "those days", "when i was", "used to"]):
            emotion_analysis["emotion"] = "nostalgic"
            emotion_analysis["suggested_color"] = "sepia"
            emotion_analysis["suggested_transparency"] = 0.8
            emotion_analysis["suggested_effects"] = ["dreamy_border", "soft_glow"]
            
        # Determination/Resolve - strong will and conviction
        elif any(phrase in dialogue_lower for phrase in ["i will", "i must", "never give up", "i'll show", "determined"]):
            emotion_analysis["emotion"] = "determined"
            emotion_analysis["intensity"] = "high"
            emotion_analysis["suggested_color"] = "orange"
            emotion_analysis["suggested_effects"] = ["bold_border", "strong_glow"]
            
        # Desperation/Panic - urgent, panicked state
        elif any(word in dialogue_lower for word in ["help", "panic", "desperate", "urgent", "hurry", "quickly"]) or \
             dialogue.count("!") >= 3:
            emotion_analysis["emotion"] = "desperate"
            emotion_analysis["intensity"] = "high"
            emotion_analysis["suggested_color"] = "bright_red"
            emotion_analysis["suggested_transparency"] = 0.9
            emotion_analysis["suggested_effects"] = ["shaky_border", "urgent_glow"]
            
        # Exhaustion/Tiredness - worn out, tired
        elif any(word in dialogue_lower for word in ["tired", "exhausted", "worn out", "can't go on", "sleepy", "yawn"]):
            emotion_analysis["emotion"] = "exhausted"
            emotion_analysis["suggested_color"] = "gray"
            emotion_analysis["suggested_transparency"] = 0.6
            emotion_analysis["suggested_effects"] = ["droopy", "faded"]
            
        # Surprise/Shock - sudden realization or shock
        elif any(word in dialogue_lower for word in ["what!", "oh my", "can't believe", "shocked", "surprised", "unbelievable"]):
            emotion_analysis["emotion"] = "surprised"
            emotion_analysis["intensity"] = "high"
            emotion_analysis["suggested_color"] = "bright_yellow"
            emotion_analysis["suggested_effects"] = ["burst", "spiky_border"]
            
        # Jealousy/Envy - envious feelings (improve detection)
        elif any(phrase in dialogue_lower for phrase in ["jealous", "envy", "why them", "why do they", "not fair", "wish i had"]):
            emotion_analysis["emotion"] = "jealous"
            emotion_analysis["suggested_color"] = "dark_green"
            emotion_analysis["suggested_transparency"] = 0.8
            emotion_analysis["suggested_effects"] = ["jagged_border", "dark_shadow"]
            
        # Guilt/Shame - feeling guilty or ashamed (improve detection)
        elif any(phrase in dialogue_lower for phrase in ["my fault", "i'm sorry", "shouldn't have", "feel guilty", "ashamed", "i should have"]):
            emotion_analysis["emotion"] = "guilty"
            emotion_analysis["suggested_color"] = "dark_blue"
            emotion_analysis["suggested_transparency"] = 0.7
            emotion_analysis["suggested_effects"] = ["curved_down", "shadow"]
            
        # Hope/Optimism - positive outlook
        elif any(word in dialogue_lower for word in ["hope", "maybe", "perhaps", "could be", "optimistic", "bright side"]):
            emotion_analysis["emotion"] = "hopeful"
            emotion_analysis["suggested_color"] = "light_yellow"
            emotion_analysis["suggested_effects"] = ["gentle_glow", "upward_curve"]
            
        # Angry/Aggressive - check first for strongest emotions
        elif any(word in dialogue_lower for word in ["angry", "mad", "furious", "hate", "rage", "pissed"]):
            emotion_analysis["emotion"] = "angry"
            emotion_analysis["intensity"] = "high"
            emotion_analysis["suggested_color"] = "red"
            emotion_analysis["suggested_effects"] = ["jagged_border"]
            
        # Fear/Terror - high priority emotional state
        elif any(word in dialogue_lower for word in ["scary", "fear", "terrified", "ghost", "monster", "afraid", "frightened"]):
            emotion_analysis["emotion"] = "fearful"
            emotion_analysis["suggested_color"] = "dark_purple"
            emotion_analysis["suggested_transparency"] = 0.9
            emotion_analysis["suggested_effects"] = ["shadow"]
            
        # Sadness - distinctive emotional state (enhanced detection)
        elif any(word in dialogue_lower for word in ["sad", "sorry", "depressed", "down", "cry", "grief", "miserable", "heartbroken", "weep"]):
            emotion_analysis["emotion"] = "sad"
            emotion_analysis["suggested_color"] = "blue"
            emotion_analysis["suggested_transparency"] = 0.8
            emotion_analysis["suggested_effects"] = ["tear_drop", "droopy"]
            
        # Romance/Love - specific emotional context
        elif any(word in dialogue_lower for word in ["love", "heart", "romantic", "sweet", "dear", "darling", "honey"]):
            emotion_analysis["emotion"] = "romantic"
            emotion_analysis["suggested_color"] = "pink"
            emotion_analysis["suggested_effects"] = ["soft_glow"]
            
        # Secretive/Whisper - check for whisper patterns
        elif (any(word in dialogue_lower for word in ["whisper", "shh", "quiet", "secret"]) or 
              dialogue.startswith("psst") or "..." in dialogue):
            emotion_analysis["emotion"] = "secretive"
            emotion_analysis["suggested_color"] = "semi_transparent"
            emotion_analysis["suggested_transparency"] = 0.6
            emotion_analysis["suggested_effects"] = ["dashed_border"]
            
        # Confusion - question marks and confused words (but avoid simple greetings)
        elif ("?" in dialogue and not any(phrase in dialogue_lower for phrase in ["how are you", "hello there"])) or \
             any(word in dialogue_lower for word in ["confused", "huh", "what", "don't understand", "puzzled"]):
            emotion_analysis["emotion"] = "confused"
            emotion_analysis["suggested_color"] = "light_blue"
            emotion_analysis["suggested_transparency"] = 0.9
            
        # Multiple exclamation marks often indicate shouting/excitement
        elif dialogue.count("!") > 1:
            emotion_analysis["emotion"] = "excited"
            emotion_analysis["intensity"] = "high"
            emotion_analysis["suggested_color"] = "yellow"
            emotion_analysis["suggested_effects"] = ["glow"]
            
        return emotion_analysis

    def _get_intelligent_color(self, bubble_color: str, style: str, dialogue: str, auto_enhance: bool) -> dict:
        """Determine the optimal color and effects based on context."""
        
        if bubble_color != "auto" and not auto_enhance:
            return {
                "color": bubble_color,
                "transparency": 1.0,
                "effects": []
            }
        
        # Analyze dialogue for emotional context
        emotion_data = self._analyze_dialogue_emotion(dialogue)
        
        # Style-specific color preferences
        style_colors = {
            "classic": "white",
            "thought": "light_blue", 
            "shout": "yellow",
            "whisper": "semi_transparent",
            "narration": "cream"
        }
        
        # Determine final color
        if bubble_color == "auto":
            if auto_enhance:
                final_color = emotion_data["suggested_color"]
            else:
                final_color = style_colors.get(style, "white")
        else:
            final_color = bubble_color
            
        return {
            "color": final_color,
            "transparency": emotion_data.get("suggested_transparency", 1.0),
            "effects": emotion_data.get("suggested_effects", []),
            "emotion": emotion_data["emotion"],
            "intensity": emotion_data["intensity"]
        }

    def _get_bubble_style_prompt(self, style: str, color_data: dict, size: str) -> str:
        """Generate detailed prompt for specific bubble styles with intelligent color selection."""
        
        color = color_data["color"]
        transparency = color_data["transparency"]
        effects = color_data.get("effects", [])
        
        # Enhanced color descriptions
        color_descriptions = {
            "white": "clean white",
            "yellow": "bright yellow with warm undertones",
            "blue": "soft blue",
            "light_blue": "pale light blue",
            "pink": "gentle pink",
            "green": "fresh green",
            "red": "vibrant red",
            "dark_purple": "deep purple",
            "cream": "warm cream",
            "semi_transparent": "semi-transparent white",
            "transparent": "nearly transparent"
        }
        
        color_desc = color_descriptions.get(color, color)
        
        # Add transparency information
        if transparency < 1.0:
            if transparency < 0.5:
                transparency_desc = "highly transparent"
            elif transparency < 0.8:
                transparency_desc = "semi-transparent"
            else:
                transparency_desc = "slightly transparent"
            color_desc = f"{transparency_desc} {color_desc}"
        
        # Base style prompts with enhanced color integration
        style_prompts = {
            "classic": f"a {color_desc} speech bubble with smooth rounded edges and a subtle border",
            "thought": f"a fluffy cloud-like thought bubble in {color_desc} with small circular dots leading to the character",
            "shout": f"a dynamic {color_desc} speech bubble with jagged, spiky edges indicating loud speech or yelling",
            "whisper": f"a small {color_desc} speech bubble with a dotted or dashed border indicating quiet speech",
            "narration": f"a rectangular {color_desc} text box with clean borders for narrative text"
        }
        
        size_specs = {
            "small": "compact and space-efficient",
            "medium": "appropriately sized for the text length", 
            "large": "prominently sized for emphasis"
        }
        
        base_style = style_prompts.get(style, style_prompts["classic"])
        size_spec = size_specs.get(size, size_specs["medium"])
        
        # Add special effects
        effect_descriptions = []
        if "glow" in effects:
            effect_descriptions.append("with a subtle glowing effect")
        if "soft_glow" in effects:
            effect_descriptions.append("with a soft, romantic glow")
        if "shadow" in effects:
            effect_descriptions.append("with a subtle shadow effect")
        if "jagged_border" in effects:
            effect_descriptions.append("with extra jagged, aggressive borders")
        if "dashed_border" in effects:
            effect_descriptions.append("with a dashed, secretive border style")
            
        effects_text = " ".join(effect_descriptions)
        
        return f"{base_style}, {size_spec}{' ' + effects_text if effects_text else ''}"

    def _get_positioning_prompt(self, position: str) -> str:
        """Generate positioning guidance for bubble placement."""
        
        position_prompts = {
            "left": "positioned on the left side of the panel, typically near a character on the left",
            "right": "positioned on the right side of the panel, typically near a character on the right",
            "center": "positioned in the upper-center area of the panel",
            "auto": "positioned optimally to avoid covering characters' faces or important visual elements"
        }
        
        return position_prompts.get(position, position_prompts["auto"])

    def _split_dialogue_for_multiple_bubbles(self, dialogue: str) -> List[str]:
        """Split long dialogue into multiple bubble-sized chunks."""
        
        # Target ~25-30 characters per bubble for readability
        target_length = 25
        words = dialogue.split()
        bubbles = []
        current_bubble = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > target_length and current_bubble:
                bubbles.append(" ".join(current_bubble))
                current_bubble = [word]
                current_length = len(word)
            else:
                current_bubble.append(word)
                current_length += len(word) + 1
        
        if current_bubble:
            bubbles.append(" ".join(current_bubble))
        
        return bubbles

    def _generate_speech_bubble_prompt(
        self, 
        dialogue: str, 
        style: str, 
        position: str, 
        color_data: dict, 
        size: str, 
        multiple: bool
    ) -> str:
        """Generate comprehensive prompt for adding speech bubbles with intelligent styling."""
        
        # Handle multiple bubbles if requested and text is long
        if multiple and len(dialogue) > 30:
            dialogue_parts = self._split_dialogue_for_multiple_bubbles(dialogue)
            dialogue_text = f"multiple speech bubbles containing: {' | '.join(dialogue_parts)}"
        else:
            dialogue_text = f"the text '{dialogue}'"
        
        bubble_style = self._get_bubble_style_prompt(style, color_data, size)
        positioning = self._get_positioning_prompt(position)
        
        # Add context-aware enhancements
        emotion = color_data.get("emotion", "neutral")
        intensity = color_data.get("intensity", "medium")
        
        emotion_guidance = ""
        if emotion == "excited":
            emotion_guidance = "- Make the bubble vibrant and energetic to match the excited tone\n"
        elif emotion == "angry":
            emotion_guidance = "- Use bold, aggressive styling to convey anger or intensity\n"
        elif emotion == "sad":
            emotion_guidance = "- Apply softer, more muted styling to reflect the somber mood\n"
        elif emotion == "secretive":
            emotion_guidance = "- Create a subtle, mysterious appearance for whispered secrets\n"
        elif emotion == "romantic":
            emotion_guidance = "- Add gentle, warm styling to enhance the romantic feeling\n"
        elif emotion == "fearful":
            emotion_guidance = "- Use darker, more ominous styling to convey fear or tension\n"
        
        prompt = f"""Add {bubble_style} containing {dialogue_text} to this comic panel.

CRITICAL REQUIREMENTS:
- Use clear, perfectly readable black text in a clean comic book font
- Ensure ALL text is spelled correctly and matches the input exactly
- Text should be well-spaced and easy to read
- Position the bubble(s) {positioning}
- Do NOT cover characters' faces or crucial visual elements
- Maintain professional comic book quality and styling
- Ensure bubbles look naturally integrated, not pasted on
- Keep the original art style and color scheme intact
- Use proper comic book text formatting with appropriate letter spacing
{emotion_guidance}- Pay attention to the emotional context and make the bubble complement the dialogue's mood

The speech bubble(s) should look indistinguishable from professional comic book dialogue with intelligent color choices that enhance the storytelling."""
        
        return prompt

    def _run(
        self,
        panel_image_path: str,
        dialogue_text: str,
        bubble_style: str = "classic",
        character_position: str = "auto",
        panel_number: int = 1,
        text_size: str = "medium",
        bubble_color: str = "auto",
        transparency: float = 1.0,
        color_intensity: str = "medium",
        auto_enhance: bool = True,
        multiple_bubbles: bool = False
    ) -> str:
        """
        Add speech bubbles to a comic panel with intelligent color selection.
        
        Args:
            panel_image_path: Path to the existing comic panel
            dialogue_text: Text to include in speech bubble(s)
            bubble_style: Style of bubble (classic, thought, shout, whisper, narration)
            character_position: Positioning hint (left, right, center, auto)
            panel_number: Panel number for file organization
            text_size: Size of text (small, medium, large)
            bubble_color: Color of bubble background ('auto' for intelligent selection)
            transparency: Transparency level (0.0 to 1.0)
            color_intensity: Color intensity (light, medium, dark)
            auto_enhance: Enable automatic color and style enhancement
            multiple_bubbles: Whether to split long text into multiple bubbles
            
        Returns:
            Success message with new filename or error message
        """
        
        print(f"💬 SpeechBubbleTool: Adding '{bubble_style}' bubble to panel {panel_number}")
        print(f"   Text: '{dialogue_text}' (length: {len(dialogue_text)} chars)")
        print(f"   Style: {bubble_style}, Position: {character_position}, Size: {text_size}")
        
        # Get intelligent color selection
        color_data = self._get_intelligent_color(bubble_color, bubble_style, dialogue_text, auto_enhance)
        if auto_enhance:
            print(f"   🎨 Auto-enhanced: {color_data['emotion']} emotion detected")
            print(f"   🎨 Color choice: {color_data['color']} (transparency: {color_data['transparency']:.1f})")
            if color_data['effects']:
                print(f"   ✨ Effects: {', '.join(color_data['effects'])}")
        
        try:
            # Validate inputs
            panel_path = Path(panel_image_path)
            if not panel_path.exists():
                return f"❌ Panel image not found: {panel_image_path}"
            
            if not dialogue_text or dialogue_text.strip() == "":
                return f"❌ dialogue_text cannot be empty"
            
            if len(dialogue_text) > 300:
                return f"❌ Dialogue text too long ({len(dialogue_text)} chars). Maximum 300 characters."
            
            # Prepare image for Gemini access
            gemini_paths = prepare_temp_images_for_gemini([str(panel_path.resolve())], "temp_speech_bubble")
            if not gemini_paths:
                return f"❌ Failed to prepare panel for Gemini access: {panel_image_path}"

            # Generate the specialized prompt with intelligent styling
            speech_prompt = self._generate_speech_bubble_prompt(
                dialogue_text, bubble_style, character_position, 
                color_data, text_size, multiple_bubbles
            )
            
            # Prepare API payload
            payload = {
                "prompt": speech_prompt,
                "base_image_paths": gemini_paths
            }

            print(f"🔄 Sending request to Gemini Image Server...")
            response = requests.post(self.server_url, json=payload, timeout=120)

            if response.status_code != 200:
                return f"❌ Server error: HTTP {response.status_code} - {response.text}"

            result = response.json()
            if result.get("status") != "success" or "image_path" not in result:
                error_message = (
                    result.get("message") or 
                    result.get("detail") or 
                    result.get("error") or 
                    "Unknown error from speech bubble generation"
                )
                return f"❌ Speech bubble generation failed: {error_message}"

            # Process the generated image
            source_path = resolve_image_path(result["image_path"])
            if not retry_file_check(source_path):
                return f"❌ Generated speech bubble panel not found: {source_path}"

            if not verify_image_readable(source_path):
                return f"❌ Generated speech bubble panel unreadable: {source_path}"

            # Create descriptive filename
            timestamp = int(time.time() * 1000)
            safe_text = "".join(c for c in dialogue_text[:20] if c.isalnum() or c in " -_").strip()
            safe_text = safe_text.replace(" ", "_")
            
            filename = f"speech_bubble_{bubble_style}_panel_{panel_number:03d}_{safe_text}_{timestamp}.png"
            
            # Copy to output directories
            panel_id = f"panel_{panel_number}"
            try:
                backend_path, frontend_path = copy_image_to_output(source_path, filename)
                update_registry_for_image(panel_id, filename, True, True)
                
                print(f"✅ Speech bubble panel saved: {filename}")
                return f"✅ Speech bubble added successfully: {filename} (backend + frontend)"
                
            except Exception as frontend_error:
                print(f"⚠️ Frontend copy failed: {frontend_error}")
                update_registry_for_image(panel_id, filename, True, False)
                return f"✅ Speech bubble added: {filename} (backend only)"

        except Exception as e:
            error_msg = f"❌ Error adding speech bubble: {str(e)}"
            print(error_msg)
            return error_msg
        
        finally:
            # Clean up temporary files
            try:
                if 'gemini_paths' in locals():
                    for temp_path in gemini_paths:
                        temp_file = Path(temp_path)
                        if temp_file.exists():
                            temp_file.unlink()
                            print(f"🧹 Cleaned up temporary file: {temp_path}")
            except Exception as cleanup_error:
                print(f"⚠️ Failed to clean up temporary files: {cleanup_error}")


# Convenience functions for common use cases with intelligent enhancement
def add_classic_speech_bubble(panel_path: str, dialogue: str, panel_num: int = 1, auto_enhance: bool = True) -> str:
    """Quick function to add a classic speech bubble with intelligent color selection."""
    tool = SpeechBubbleTool()
    return tool._run(panel_path, dialogue, "classic", "auto", panel_num, auto_enhance=auto_enhance)


def add_thought_bubble(panel_path: str, thought: str, panel_num: int = 1, auto_enhance: bool = True) -> str:
    """Quick function to add a thought bubble with intelligent styling."""
    tool = SpeechBubbleTool()
    return tool._run(panel_path, thought, "thought", "auto", panel_num, auto_enhance=auto_enhance)


def add_shout_bubble(panel_path: str, shout_text: str, panel_num: int = 1, auto_enhance: bool = True) -> str:
    """Quick function to add a shout/exclamation bubble with dynamic styling.""" 
    tool = SpeechBubbleTool()
    return tool._run(panel_path, shout_text, "shout", "auto", panel_num, auto_enhance=auto_enhance)


def add_emotional_bubble(panel_path: str, dialogue: str, panel_num: int = 1) -> str:
    """Add a speech bubble with maximum auto-enhancement for emotional context."""
    tool = SpeechBubbleTool()
    return tool._run(panel_path, dialogue, "classic", "auto", panel_num, 
                    bubble_color="auto", auto_enhance=True)