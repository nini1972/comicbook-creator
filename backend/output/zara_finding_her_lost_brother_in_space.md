Thought: I need to extract the panel descriptions, dialogue, and image paths from the provided context to create the final comic layout. I will then use the `Comic Layout Designer` tool to assemble these elements into a markdown comic strip.

1.  **Panel Descriptions**: I will extract the detailed descriptions for each of the five panels from the "Comic Script".
2.  **Dialogue**: I will extract the dialogue, captions, and sound effects for each panel.
3.  **Image Paths**: I will take the list of "Successfully Generated Image Paths" and format them correctly for the web (e.g., `output/comic_panels/image.png` becomes `/comic_panels/image.png`). I will use `null` or an equivalent placeholder for the failed Panel 2 image.
4.  **Tool Call**: I will assemble these three lists and pass them to the `Comic Layout Designer` tool.
5.  **Final Output**: I will return only the markdown output from the tool as the final answer, as instructed.```markdown
# Comic: The Ghost Signal

*A hardened space scavenger, haunted by the past, follows a faint signal into a ship graveyard, hoping to find her brother who was lost five years ago.*

---

### **Panel 1**

A wide, establishing shot. ZARA's small, rugged ship, the "MAGPIE," drifts in the silent void. It is dwarfed by the scene before it: a massive, tangled graveyard of colossal, derelict spaceships from a forgotten era. The metal skeletons are caught in the gravitational pull of a swirling, purple and blue nebula in the background, which provides a beautiful yet haunting light source.

![Panel 1: Establishing shot of Magpie in a spaceship graveyard, dwarfed by a nebula.](/comic_panels/server_generated_gemini-image-tutorial_1757952460655.png)

**CAPTION:** The Ghost Signal. A whisper in the static. For five years, it was all she had.

---

### **Panel 2**

Interior of a derelict ship. A tight, close-up shot focusing on ZARA's gloved hand. She is gently touching a crude drawing etched into a rusted metal wall. The drawing shows two stick figures—one tall, one small—holding hands under two suns. The light from her helmet's lamp illuminates the etching and the determined, yet fragile, hope in her visible eye.

**ZARA (V.O., a whisper):** Leo...

---

### **Panel 3**

Medium shot. ZARA stands in a vast, dark chamber. Debris floats in zero-gravity around her. Her headlamp cuts a sharp beam through the darkness, landing on the source of the signal: a single, frost-covered cryo-stasis pod standing upright against a far wall. A small console on the pod is blinking with a soft, steady blue light, a beacon in the gloom. Her posture is tense with anticipation and fear.

![Panel 3: Zara finds the cryo-pod.](/comic_panels/consistent_panel_003_zara.png)

**ZARA (To herself, voice tight):** Don't be another ghost. Please... don't be another ghost.

---

### **Panel 4**

A split panel showing two moments in quick succession. Top Half: Close-up on Zara’s face, her reflection visible in the frosty glass of the pod. Her brow is furrowed in concentration as her fingers fly across the activation panel. Bottom Half: A wider view of the pod as the main seal breaks. A loud hiss of escaping gas erupts, billowing out in a thick white cloud. Inside the mist, the small silhouette of a child, LEO, is visible, his eyes beginning to flutter open.

![Panel 4: Split panel showing pod activation and Leo waking up.](/comic_panels/consistent_panel_004_zara.png)

**SFX:** HSSSSSSSSSSHHHH
**LEO (Weakly, confused):** …Zara?

---

### **Panel 5**

Full-width, emotional final panel. The interior of the Magpie's cockpit. ZARA has her helmet off, revealing short, messy hair and tear streaks on her grime-smudged cheeks. She is on her knees, tightly hugging LEO, who is wrapped in a thermal blanket. He is small and frail, burying his face in her shoulder, hugging her back. Behind them, through the large cockpit viewport, the beautiful, star-dusted nebula fills the frame, symbolizing a new, uncertain dawn.

![Panel 5: Zara and Leo reunited in Magpie's cockpit.](/comic_panels/consistent_panel_005_zara.png)

**ZARA (Sobbing softly):** I found you. Leo, I found you.
**LEO (Muffled):** I was… I was scared. Are we going home?
**ZARA (Pulling back to look at him, a sad but determined smile):** We’ll find a new one. Together.

---
```