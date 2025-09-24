import re

# Test the panel extraction logic
test_prompts = [
    'Generate Panel 1: A comic panel showing...',
    'Create Panel 2 with a character standing...',
    'PANEL 3: Dark scene with dramatic lighting...',
    'This is for panel 4 of the comic...',
    'Generate an image for comic panel 5',
    'No panel mentioned here'
]

print('Testing panel number extraction from prompts:')
print('=' * 60)

for prompt in test_prompts:
    panel_match = re.search(r'panel\s*(\d+)', prompt.lower())
    if panel_match:
        panel_number = panel_match.group(1)
        panel_id = f'panel_{panel_number}'
        print(f'✅ "{prompt[:40]}..." -> {panel_id}')
    else:
        print(f'❌ "{prompt[:40]}..." -> No panel found')