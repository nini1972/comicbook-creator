from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

def mask(k):
    v = os.getenv(k)
    return (v[:3] + '...') if v else None

print('Masked keys:', {'OPENAI_API_KEY': mask('OPENAI_API_KEY'), 'GOOGLE_API_KEY': mask('GOOGLE_API_KEY'), 'GEMINI_API_KEY': mask('GEMINI_API_KEY')})

import litellm
try:
    # Use chat-style messages to satisfy OpenAI chat API expectations
    resp = litellm.completion(model='gpt-4o-mini', messages=[{"role": "user", "content": "Say hi and return OK in one short line."}], max_tokens=16)
    print('Probe succeeded. Response:')
    # print a concise representation
    try:
        print(resp.choices[0].message['content'])
    except Exception:
        print(str(resp))
except Exception as e:
    print('Probe failed:', type(e).__name__, str(e))
    raise
