from visual_comic_crew.tools.comic_layout_tool import ComicLayoutTool, ComicLayoutInput

# Dummy panel descriptions and dialogue
panels = [
    "A robot wakes up in a neon-lit lab.",
    "It gazes at a photo of a human family.",
    "The robot steps outside into a rainy cityscape."
]

dialogue = [
    "Where... am I?",
    "Is this what love looks like?",
    "Time to find out who I really am."
]

# Simulate image paths (these don't need to exist for markdown generation)
image_paths = [
    "backend/output/comic_panels/server_generated_gemini-image-tutorial_1759235427051.png",
    "backend/output/comic_panels/server_generated_gemini-image-tutorial_1759235491762.png",
    "backend/output/comic_panels/server_generated_gemini-image-tutorial_1759235550894.png"
]

# Create input and tool instance
input_data = ComicLayoutInput(panels=panels, dialogue=dialogue, image_paths=image_paths)
tool = ComicLayoutTool()

# Run the tool
markdown_output = tool._run(**input_data.dict())

# Print the result
print("\n=== Generated Markdown ===\n")
print(markdown_output)