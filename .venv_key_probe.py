import os, json
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def masked(s):
    return (s[:3] + '...') if s and len(s)>3 else (s + '...')

candidates = [
    'GOOGLE_API_KEY',
    'GOOGLE_GENAI_API_KEY',
    'GOOGLE_GENERATIVE_API_KEY',
    'GENAI_API_KEY',
    'LITELLM_API_KEY',
]
key = None
key_name = None
for n in candidates:
    v = os.environ.get(n)
    if v:
        key = v.strip()
        key_name = n
        break
print('Key probe: selected env var ->', key_name if key_name else 'NONE')
if not key:
    print('No key found in environment candidates.')
    raise SystemExit(1)
print('Masked key prefix:', masked(key))

# perform a minimal GET to list models; don't print key
import json
try:
    import httpx
    client = httpx.Client(timeout=10.0)
    url = 'https://generativelanguage.googleapis.com/v1beta/models?key=' + key
    r = client.get(url)
    status = r.status_code
    txt = r.text
    client.close()
except Exception as e:
    # fallback to urllib
    try:
        import urllib.request
        url = 'https://generativelanguage.googleapis.com/v1beta/models?key=' + key
        with urllib.request.urlopen(url, timeout=10) as resp:
            status = resp.getcode()
            txt = resp.read(1024).decode('utf-8', errors='replace')
    except Exception as e2:
        print('HTTP request failed:', str(e2))
        raise SystemExit(2)

print('HTTP status:', status)
# print a short safe excerpt
excerpt = txt.strip().replace('\n',' ')[:800]
if excerpt:
    print('Response excerpt:', excerpt)
else:
    print('Response empty')
