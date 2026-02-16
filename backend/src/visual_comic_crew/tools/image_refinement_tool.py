import os
from pathlib import Path
from typing import Optional, Type, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests
import time
from src.utils.image_utils import (
    resolve_image_path,
    retry_file_check,
    verify_image_readable,
    copy_image_to_output,
    update_registry_for_image,
    prepare_temp_images_for_gemini,
    clean_temp_folder
)

class ImageRefinementToolSchema(BaseModel):
    """Input schema for Image Refinement Tool."""
    base_image_path: str = Field(..., description="Path to the base image to refine")
    refinement_prompt: str = Field(..., description="Description of how to refine or modify the image")
    panel_number: int = Field(1, description="Panel number for scene generation")
    # Speech bubble functionality
    add_speech_bubble: bool = Field(False, description="Whether to add a speech bubble with dialogue text")
    dialogue_text: Optional[str] = Field(None, description="Text to include in speech bubble (required if add_speech_bubble=True)")
    bubble_style: str = Field("classic", description="Style of speech bubble: 'classic' (white), 'thought' (cloud), 'shout' (jagged), 'whisper' (small)")
    character_position: str = Field("auto", description="Character position for bubble placement: 'left', 'right', 'center', 'auto'")

class ImageRefinementTool(BaseTool):
    name: str = "Image Refinement Tool"
    description: str = (
        "Refines and modifies existing comic panel images using Gemini's image editing "
        "capabilities. Can apply style transfers, make adjustments, fine-tune panels, "
        "and ADD SPEECH BUBBLES with dialogue text. Use this when you need to "
        "modify an existing image rather than generate a new one from scratch. "
        "NEW: Set add_speech_bubble=True and provide dialogue_text to automatically "
        "add comic-style speech bubbles to your panels with professional text formatting."
    )
    args_schema: Type[BaseModel] = ImageRefinementToolSchema
    server_url: str = os.getenv("GEMINI_IMAGE_SERVER_URL", "http://127.0.0.1:8000/generate-image/")

    def __init__(self):
        super().__init__()

    def _sanitize_dialogue(self, text: str) -> str:
        """Sanitize dialogue text to reduce chances of safety blocks and layout issues.

        - Collapse whitespace and newlines to single spaces
        - Trim surrounding quotes
        - Remove control characters
        - Limit repeated punctuation
        """
        if not text:
            return ""
        t = str(text).replace("\n", " ").replace("\r", " ")
        t = " ".join(t.split())  # collapse whitespace
        # strip surrounding quotes
        if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
            t = t[1:-1]
        # remove control chars
        t = "".join(ch for ch in t if ord(ch) >= 32)
        # limit repeated punctuation
        import re as _re
        t = _re.sub(r"([!?.]){3,}", r"\1\1", t)
        return t.strip()

    def _split_dialogue(self, text: str, max_len: int = 60, max_bubbles: int = 4) -> List[str]:
        """Split dialogue into multiple bubble texts.

        - Respect explicit '|' separators if present.
        - Otherwise, greedily wrap into chunks up to max_len.
        - Cap number of bubbles to max_bubbles (last chunk contains remainder).
        """
        if not text:
            return []

        t = text.strip()
        if not t:
            return []

        # Respect explicit multi-bubble separators provided by caller
        if "|" in t:
            parts = [p.strip() for p in t.split("|") if p.strip()]
            if parts:
                if len(parts) <= max_bubbles:
                    return parts
                # cap and merge the rest in the last bubble
                head = parts[:max_bubbles - 1]
                tail = [" ".join(parts[max_bubbles - 1:]).strip()]
                return head + tail

        if len(t) <= max_len:
            return [t]

        # First try splitting on punctuation into sentences
        import re as _re
        sentences = [s.strip() for s in _re.split(r"(?<=[.!?])\s+", t) if s.strip()]
        chunks: List[str] = []
        cur = ""
        for s in sentences:
            candidate = (cur + (" " if cur else "") + s).strip()
            if len(candidate) <= max_len:
                cur = candidate
            else:
                if cur:
                    chunks.append(cur)
                if len(s) <= max_len:
                    cur = s
                else:
                    # sentence longer than max_len: word-wrap it
                    words = s.split()
                    buf: List[str] = []
                    for w in words:
                        cand2 = (" ".join(buf + [w])).strip()
                        if len(cand2) <= max_len:
                            buf.append(w)
                        else:
                            chunks.append(" ".join(buf))
                            buf = [w]
                            if len(chunks) >= max_bubbles - 1:
                                break
                    if buf:
                        cur = " ".join(buf)
            if len(chunks) >= max_bubbles - 1:
                break
        if cur and len(chunks) < max_bubbles:
            chunks.append(cur)

        # If still too many pieces, merge tail into the last slot
        if len(chunks) > max_bubbles:
            head = chunks[:max_bubbles - 1]
            tail = " ".join(chunks[max_bubbles - 1:])
            chunks = head + [tail]

        return [c for c in chunks if c]

    def _generate_speech_bubble_prompt(self, dialogue: List[str], bubble_style: str, character_position: str, minimal: bool = False) -> str:
        """Generate a specialized prompt for adding one or multiple speech bubbles.

        dialogue: list of bubble texts in reading order.
        minimal: if True, produce a shorter prompt that avoids extensive requirements (fallback for safety blocks).
        """

        # Define bubble style specifications
        style_specs = {
            "classic": "a clean white speech bubble with black border",
            "thought": "a fluffy cloud-like thought bubble with small circles leading to it",
            "shout": "a jagged, dynamic speech bubble with spiky edges for shouting",
            "whisper": "a small, delicate speech bubble with VERY PROMINENT DOTTED BORDER (use clear dots or dashes, NOT solid lines) for quiet whispering",
        }

        # Define positioning guidance
        position_specs = {
            "left": "on the left side of the panel, near any character speaking from the left",
            "right": "on the right side of the panel, near any character speaking from the right", 
            "center": "near the top center of the panel, avoiding the center where characters might be",
            "auto": "in the most appropriate area near the speaking character, avoiding faces and important visual elements. For split panels or panels with multiple sections, carefully place the bubble in the section with the speaking character",
        }

        bubble_spec = style_specs.get(bubble_style, style_specs["classic"])
        position_spec = position_specs.get(character_position, position_specs["auto"])

        if minimal:
            if len(dialogue) == 1:
                return (
                    f"Add {bubble_spec} {position_spec}, containing this exact text: \"{dialogue[0]}\". "
                    f"Keep the original art style and integrate naturally."
                )
            else:
                bullets = "\n".join([f"- \"{t}\"" for t in dialogue])
                return (
                    f"Add {len(dialogue)} {bubble_style} speech bubbles {position_spec}, each with the following texts, in reading order:\n"
                    f"{bullets}\nKeep the style consistent and avoid covering faces."
                )

        # Full prompt (more guidance)
        if len(dialogue) == 1:
            text = dialogue[0]
            # Special handling for whisper bubbles
            if bubble_style == "whisper":
                prompt = f"""Add {bubble_spec} containing the exact text \"{text}\" to this comic panel.

Requirements:
- Use clear, readable black text in a smaller, delicate comic font
- The bubble border MUST be clearly dotted or dashed (NOT a solid line)
- Position the bubble {position_spec}
- Make the bubble smaller than normal speech bubbles
- Do not cover characters' faces or important visual elements
- Integrate naturally with consistent art style
- Ensure high contrast between text and bubble interior

The whisper bubble should have an obviously dotted/dashed border to indicate quiet speech."""
            else:
                prompt = f"""Add {bubble_spec} containing the exact text \"{text}\" to this comic panel.

Requirements:
- Use clear, readable black text in a clean comic font (no blur)
- Position the bubble {position_spec}
- Do not cover characters' faces or important visual elements
- Integrate naturally with consistent art style
- Proper letter spacing, high contrast for readability

The speech bubble should look like professional comic dialogue."""
            return prompt
        else:
            bullets = "\n".join([f"- \"{t}\"" for t in dialogue])
            if bubble_style == "whisper":
                prompt = f"""Add {len(dialogue)} {bubble_style} speech bubbles to this comic panel, each containing the following texts, in reading order (left-to-right, top-to-bottom):
{bullets}

Requirements:
- Use clear, readable black text in a smaller, delicate comic font
- Each bubble border MUST be clearly dotted or dashed (NOT solid lines)
- Place the bubbles {position_spec} and space them evenly
- Make bubbles smaller than normal speech bubbles for whispering effect
- Avoid covering faces or key visual details; ensure no overlap between bubbles
- Match the panel's art style; integrate naturally

The whisper bubbles should have obviously dotted/dashed borders to indicate quiet speech."""
            else:
                prompt = f"""Add {len(dialogue)} {bubble_style} speech bubbles to this comic panel, each containing the following texts, in reading order (left-to-right, top-to-bottom):
{bullets}

Requirements:
- Use clear, readable black text in a clean comic font
- Place the bubbles {position_spec} and space them evenly
- Avoid covering faces or key visual details; ensure no overlap between bubbles
- Match the panel's art style; integrate naturally

They should be indistinguishable from professional comic dialogue."""
            return prompt

    def _run(
        self,
        base_image_path: str,
        refinement_prompt: str,
        panel_number: int = 1,
        add_speech_bubble: bool = False,
        dialogue_text: Optional[str] = None,
        bubble_style: str = "classic",
        character_position: str = "auto"
    ) -> str:
        print(f"🔧 DEBUG: ImageRefinementTool called with base_image='{base_image_path}', panel={panel_number}")
        if add_speech_bubble:
            print(f"💬 DEBUG: Adding speech bubble - style='{bubble_style}', text='{dialogue_text}', position='{character_position}'")
        try:
            base_path = Path(base_image_path)
            print(f"🔍 Checking if base image exists at: {base_path.resolve()}")
            print(f"🔍 Path exists? {base_path.exists()}")
            if not base_path.exists():
                return f"❌ Base image not found: {base_image_path} (resolved: {base_path.resolve()})"

            # Validate speech bubble parameters
            if add_speech_bubble:
                if not dialogue_text or dialogue_text.strip() == "":
                    return f"❌ dialogue_text is required when add_speech_bubble=True"
                if len(dialogue_text) > 200:
                    print(f"⚠️ Warning: Long dialogue text ({len(dialogue_text)} chars) might not fit well in bubble")

            # Construct the refinement prompt
            if add_speech_bubble and dialogue_text:
                # Sanitize and split dialogue for potential multi-bubble rendering
                sanitized_text = self._sanitize_dialogue(dialogue_text)
                bubble_texts = self._split_dialogue(sanitized_text)
                if not bubble_texts:
                    return "❌ dialogue_text parsing failed or empty after processing"

                # Generate specialized speech bubble prompt (full guidance first)
                speech_bubble_prompt = self._generate_speech_bubble_prompt(bubble_texts, bubble_style, character_position)

                # Combine with any additional refinements
                if refinement_prompt and refinement_prompt.strip():
                    full_prompt = f"Panel {panel_number}: {refinement_prompt}. Also, {speech_bubble_prompt}"
                else:
                    full_prompt = f"Panel {panel_number}: {speech_bubble_prompt}"
            else:
                # Standard refinement without speech bubbles
                full_prompt = (
                    f"Panel {panel_number}: Refine and modify the existing comic panel image with these changes: "
                    f"{refinement_prompt}. Maintain the comic art style and character consistency."
                )
            # Prepare base image for Gemini access
            temp_folder = "temp_refinement_images"
            gemini_paths = prepare_temp_images_for_gemini([str(base_path.resolve())], temp_folder)

            if not gemini_paths:
                    return f"❌ Failed to prepare base image for Gemini access: {base_image_path}"

            def send_request(prompt: str, timeout_s: int = 160):
                payload = {
                    "prompt": prompt,
                    "base_image_paths": gemini_paths,
                }
                print(f"🔄 Refining image for panel {panel_number}: {base_image_path}")
                if add_speech_bubble:
                    print(f"💬 Prompt (len={len(prompt)}): {prompt[:240]}{'...' if len(prompt) > 240 else ''}")
                return requests.post(self.server_url, json=payload, timeout=timeout_s)

            # Attempt up to 3 tries with simplified prompts and backoff on failure
            prompts = [full_prompt]

            # Fallback 1: remove "Panel N:" prefix and force auto positioning
            if add_speech_bubble and dialogue_text:
                bubble_texts = self._split_dialogue(self._sanitize_dialogue(dialogue_text))
                prompts.append(self._generate_speech_bubble_prompt(bubble_texts, bubble_style, "auto"))

            # Fallback 2: minimal prompt variant
            if add_speech_bubble and dialogue_text:
                bubble_texts = self._split_dialogue(self._sanitize_dialogue(dialogue_text))
                prompts.append(self._generate_speech_bubble_prompt(bubble_texts, bubble_style, "auto", minimal=True))

            response = None
            result = None
            last_error = None
            try:
                for i, p in enumerate(prompts):
                    try:
                        response = send_request(p)
                        if response.status_code != 200:
                            last_error = f"HTTP {response.status_code} - {response.text}"
                            print(f"⚠️ Attempt {i+1} failed: {last_error}")
                            if i < len(prompts) - 1:
                                # exponential backoff with small jitter
                                import random as _rand, time as _time
                                delay = min(2 ** i, 8) + _rand.random() * 0.25
                                _time.sleep(delay)
                            continue
                        result = response.json()
                        if result.get("status") != "success" or "image_path" not in result:
                            err = (
                                result.get("message")
                                or result.get("detail")
                                or result.get("error")
                                or "Unknown error from image refinement server."
                            )
                            last_error = err
                            print(f"⚠️ Attempt {i+1} logical failure: {err}")
                            if i < len(prompts) - 1:
                                import random as _rand, time as _time
                                delay = min(2 ** i, 8) + _rand.random() * 0.25
                                _time.sleep(delay)
                            continue
                        # Success
                        break
                    except Exception as post_err:
                        last_error = str(post_err)
                        print(f"⚠️ Attempt {i+1} exception: {last_error}")
                        if i < len(prompts) - 1:
                            import random as _rand, time as _time
                            delay = min(2 ** i, 8) + _rand.random() * 0.25
                            _time.sleep(delay)
                        continue
            finally:
                # Always attempt to clean the temp folder to avoid clutter
                try:
                    clean_temp_folder(temp_folder)
                except Exception as _cleanup_err:
                    print(f"⚠️ Temp cleanup failed: {_cleanup_err}")

            if not result or result.get("status") != "success" or "image_path" not in result:
                return f"❌ Failed to refine image after {len(prompts)} attempts: {last_error}"

            source_path = resolve_image_path(result["image_path"])
            if not retry_file_check(source_path):
                return f"❌ Refined image not found after retries: {source_path}"

            if not verify_image_readable(source_path):
                return f"❌ Refined image unreadable: {source_path}"

            timestamp = int(time.time() * 1000)
            base_name = base_path.stem
            
            # Create descriptive filename based on operation type
            if add_speech_bubble:
                panel_filename = f"speech_bubble_panel_{panel_number:03d}_{base_name}_{timestamp}.png"
                operation_desc = f"speech bubble with '{dialogue_text}'"
            else:
                panel_filename = f"refined_panel_{panel_number:03d}_{base_name}_{timestamp}.png"
                operation_desc = "refinement"

            panel_id = f"panel_{panel_number}"
            try:
                backend_path, frontend_path = copy_image_to_output(source_path, panel_filename)
                update_registry_for_image(panel_id, panel_filename, True, True)
                return f"✅ Image {operation_desc} completed: {panel_filename} (copied to backend and frontend)"
            except Exception as frontend_error:
                print(f"⚠️ Frontend copy failed: {frontend_error}")
                update_registry_for_image(panel_id, panel_filename, True, False)
                return f"✅ Image {operation_desc} completed: {panel_filename} (frontend copy skipped)"

        except Exception as e:
            error_msg = f"❌ Error in image refinement: {str(e)}"
            print(error_msg)
            return error_msg
