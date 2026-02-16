#!/usr/bin/env python3
"""
Quick test script to try out the enhanced emotion detection.
Perfect for experimenting with different dialogue types.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.visual_comic_crew.tools.speech_bubble_tool import SpeechBubbleToolSchema

def test_dialogue(dialogue_text):
    """Test a single dialogue and show the emotion detection results."""
    
    try:
        # Create a mock tool instance to access the emotion analysis methods
        class QuickTestTool:
            def _analyze_dialogue_emotion(self, dialogue: str) -> dict:
                """Copy of the enhanced emotion analysis method."""
                dialogue_lower = dialogue.lower()
                
                emotion_analysis = {
                    "emotion": "neutral",
                    "intensity": "medium",
                    "suggested_color": "white",
                    "suggested_transparency": 1.0,
                    "suggested_effects": []
                }
                
                # Enhanced emotion detection logic
                if ("!" in dialogue and 
                      any(word in dialogue_lower for word in ["wow", "amazing", "great", "awesome", "fantastic", "wonderful", "incredible"]) and
                      not any(phrase in dialogue_lower for phrase in ["oh great", "just great"])):
                    emotion_analysis["emotion"] = "excited"
                    emotion_analysis["intensity"] = "high"
                    emotion_analysis["suggested_color"] = "yellow"
                    emotion_analysis["suggested_effects"] = ["glow"]
                    
                elif (dialogue.startswith("(") and dialogue.endswith(")")) or \
                   (any(phrase in dialogue_lower for phrase in ["i think", "i wonder", "maybe i", "what if"]) and
                    not any(phrase in dialogue_lower for phrase in ["shouldn't have", "my fault"])):
                    emotion_analysis["emotion"] = "inner_thought"
                    emotion_analysis["suggested_color"] = "light_gray"
                    emotion_analysis["suggested_transparency"] = 0.7
                    emotion_analysis["suggested_effects"] = ["italic_style", "soft_border"]
                    
                elif (any(phrase in dialogue_lower for phrase in ["oh great", "wonderful", "just perfect", "how lovely"]) and
                      not any(word in dialogue_lower for word in ["amazing", "incredible"])) or \
                     (dialogue.count('"') >= 2):
                    emotion_analysis["emotion"] = "sarcastic"
                    emotion_analysis["suggested_color"] = "dark_green"
                    emotion_analysis["suggested_transparency"] = 0.9
                    emotion_analysis["suggested_effects"] = ["tilted", "air_quotes"]
                    
                elif any(phrase in dialogue_lower for phrase in ["i remember", "back then", "those days", "when i was", "used to"]):
                    emotion_analysis["emotion"] = "nostalgic"
                    emotion_analysis["suggested_color"] = "sepia"
                    emotion_analysis["suggested_transparency"] = 0.8
                    emotion_analysis["suggested_effects"] = ["dreamy_border", "soft_glow"]
                    
                elif any(phrase in dialogue_lower for phrase in ["i will", "i must", "never give up", "i'll show", "determined"]):
                    emotion_analysis["emotion"] = "determined"
                    emotion_analysis["intensity"] = "high"
                    emotion_analysis["suggested_color"] = "orange"
                    emotion_analysis["suggested_effects"] = ["bold_border", "strong_glow"]
                    
                elif any(word in dialogue_lower for word in ["help", "panic", "desperate", "urgent", "hurry", "quickly"]) or \
                     dialogue.count("!") >= 3:
                    emotion_analysis["emotion"] = "desperate"
                    emotion_analysis["intensity"] = "high"
                    emotion_analysis["suggested_color"] = "bright_red"
                    emotion_analysis["suggested_transparency"] = 0.9
                    emotion_analysis["suggested_effects"] = ["shaky_border", "urgent_glow"]
                    
                elif any(word in dialogue_lower for word in ["tired", "exhausted", "worn out", "can't go on", "sleepy", "yawn"]):
                    emotion_analysis["emotion"] = "exhausted"
                    emotion_analysis["suggested_color"] = "gray"
                    emotion_analysis["suggested_transparency"] = 0.6
                    emotion_analysis["suggested_effects"] = ["droopy", "faded"]
                    
                elif any(word in dialogue_lower for word in ["what!", "oh my", "can't believe", "shocked", "surprised", "unbelievable"]):
                    emotion_analysis["emotion"] = "surprised"
                    emotion_analysis["intensity"] = "high"
                    emotion_analysis["suggested_color"] = "bright_yellow"
                    emotion_analysis["suggested_effects"] = ["burst", "spiky_border"]
                    
                elif any(phrase in dialogue_lower for phrase in ["jealous", "envy", "why them", "why do they", "not fair", "wish i had"]):
                    emotion_analysis["emotion"] = "jealous"
                    emotion_analysis["suggested_color"] = "dark_green"
                    emotion_analysis["suggested_transparency"] = 0.8
                    emotion_analysis["suggested_effects"] = ["jagged_border", "dark_shadow"]
                    
                elif any(phrase in dialogue_lower for phrase in ["my fault", "i'm sorry", "shouldn't have", "feel guilty", "ashamed", "i should have"]):
                    emotion_analysis["emotion"] = "guilty"
                    emotion_analysis["suggested_color"] = "dark_blue"
                    emotion_analysis["suggested_transparency"] = 0.7
                    emotion_analysis["suggested_effects"] = ["curved_down", "shadow"]
                    
                elif any(word in dialogue_lower for word in ["hope", "maybe", "perhaps", "could be", "optimistic", "bright side"]):
                    emotion_analysis["emotion"] = "hopeful"
                    emotion_analysis["suggested_color"] = "light_yellow"
                    emotion_analysis["suggested_effects"] = ["gentle_glow", "upward_curve"]
                    
                elif any(word in dialogue_lower for word in ["angry", "mad", "furious", "hate", "rage", "pissed"]):
                    emotion_analysis["emotion"] = "angry"
                    emotion_analysis["intensity"] = "high"
                    emotion_analysis["suggested_color"] = "red"
                    emotion_analysis["suggested_effects"] = ["jagged_border"]
                    
                elif any(word in dialogue_lower for word in ["scary", "fear", "terrified", "ghost", "monster", "afraid", "frightened"]):
                    emotion_analysis["emotion"] = "fearful"
                    emotion_analysis["suggested_color"] = "dark_purple"
                    emotion_analysis["suggested_transparency"] = 0.9
                    emotion_analysis["suggested_effects"] = ["shadow"]
                    
                elif any(word in dialogue_lower for word in ["sad", "sorry", "depressed", "down", "cry", "grief", "miserable", "heartbroken", "weep"]):
                    emotion_analysis["emotion"] = "sad"
                    emotion_analysis["suggested_color"] = "blue"
                    emotion_analysis["suggested_transparency"] = 0.8
                    emotion_analysis["suggested_effects"] = ["tear_drop", "droopy"]
                    
                elif any(word in dialogue_lower for word in ["love", "heart", "romantic", "sweet", "dear", "darling", "honey"]):
                    emotion_analysis["emotion"] = "romantic"
                    emotion_analysis["suggested_color"] = "pink"
                    emotion_analysis["suggested_effects"] = ["soft_glow"]
                    
                elif (any(word in dialogue_lower for word in ["whisper", "shh", "quiet", "secret"]) or 
                      dialogue.startswith("psst") or "..." in dialogue):
                    emotion_analysis["emotion"] = "secretive"
                    emotion_analysis["suggested_color"] = "semi_transparent"
                    emotion_analysis["suggested_transparency"] = 0.6
                    emotion_analysis["suggested_effects"] = ["dashed_border"]
                    
                elif ("?" in dialogue and not any(phrase in dialogue_lower for phrase in ["how are you", "hello there"])) or \
                     any(word in dialogue_lower for word in ["confused", "huh", "what", "don't understand", "puzzled"]):
                    emotion_analysis["emotion"] = "confused"
                    emotion_analysis["suggested_color"] = "light_blue"
                    emotion_analysis["suggested_transparency"] = 0.9
                    
                elif dialogue.count("!") > 1:
                    emotion_analysis["emotion"] = "excited"
                    emotion_analysis["intensity"] = "high"
                    emotion_analysis["suggested_color"] = "yellow"
                    emotion_analysis["suggested_effects"] = ["glow"]
                    
                return emotion_analysis
        
        tool = QuickTestTool()
        
        # Analyze the emotion
        emotion_result = tool._analyze_dialogue_emotion(dialogue_text)
        
        print(f"\n📝 Testing: '{dialogue_text}'")
        print(f"🎭 Emotion: {emotion_result['emotion']}")
        print(f"🎨 Color: {emotion_result['suggested_color']}")
        print(f"🔍 Transparency: {emotion_result.get('suggested_transparency', 1.0)}")
        effects = emotion_result.get('suggested_effects', [])
        if effects:
            print(f"✨ Effects: {', '.join(effects)}")
        else:
            print(f"✨ Effects: None")
        
    except Exception as e:
        print(f"❌ Error testing dialogue: {e}")
        print(f"💡 Fallback: Testing basic emotion patterns...")
        
        # Simple fallback
        dialogue_lower = dialogue_text.lower()
        
        if dialogue_text.startswith("(") and dialogue_text.endswith(")"):
            emotion, color = "inner_thought", "light_gray"
        elif "great" in dialogue_lower and "oh" in dialogue_lower:
            emotion, color = "sarcastic", "dark_green"
        elif any(word in dialogue_lower for word in ["sad", "heartbroken", "cry"]):
            emotion, color = "sad", "blue"
        elif "!" in dialogue_text and any(word in dialogue_lower for word in ["amazing", "wonderful"]):
            emotion, color = "excited", "yellow"
        elif any(word in dialogue_lower for word in ["angry", "furious", "mad"]):
            emotion, color = "angry", "red"
        else:
            emotion, color = "neutral", "white"
            
        print(f"\n📝 Testing: '{dialogue_text}'")
        print(f"🎭 Emotion: {emotion} (basic detection)")
        print(f"🎨 Color: {color}")

def main():
    """Interactive test for trying different dialogue types."""
    
    print("🎪 Enhanced Speech Bubble Emotion Tester 🎪")
    print("=" * 50)
    print("Try different types of dialogue to see emotion detection in action!")
    print("Type 'quit' to exit\n")
    
    # Show some example dialogues to try
    examples = [
        "(I wonder if this will work)",  # inner thought
        "Oh great, another meeting...",   # sarcasm
        "I remember when we were kids",   # nostalgia
        "I will never give up!",          # determination
        "Help! This is urgent!",          # desperation
        "I'm so tired...",                # exhaustion
        "What! I can't believe it!",      # surprise
        "Why do they get everything?",    # jealousy
        "This is all my fault",           # guilt
        "Maybe tomorrow will be better",  # hope
        "I'm furious about this!",        # anger
        "This is amazing!",               # excitement
        "That ghost scares me",           # fear
        "I love you so much",             # romance
        "Psst, keep this secret",         # secretive
        "Huh? What's happening?",         # confused
        "I feel so heartbroken"           # sadness
    ]
    
    print("📚 Example dialogues to try:")
    for i, example in enumerate(examples, 1):
        print(f"{i:2d}. {example}")
    
    print("\n" + "=" * 50)
    
    while True:
        try:
            user_input = input("\n💬 Enter dialogue (or 'quit'): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for testing! Goodbye!")
                break
                
            if not user_input:
                print("Please enter some dialogue to test!")
                continue
                
            test_dialogue(user_input)
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for testing! Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()