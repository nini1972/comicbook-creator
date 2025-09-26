import os, json
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
candidates = [
    'GOOGLE_API_KEY',
    'GOOGLE_GENERATIVE_API_KEY',
    'GENAI_API_KEY',
    'GOOGLE_GENAI_API_KEY',
    'LITELLM_API_KEY',
    'OPENAI_API_KEY',
    'GOOGLE_APPLICATION_CREDENTIALS',
]
print('Masked env diagnostic (values masked, types heuristics):')
for name in candidates:
    val = os.environ.get(name)
    if val is None:
        print(f"- {name}: NOT SET")
        continue
    v = val.strip()
    # Masking: show first 3 chars
    preview = (v[:3] + '...') if len(v) > 3 else (v + '...')
    kind = 'unknown'
    extra = ''
    # heuristic: JSON
    if v.startswith('{') and '"type"' in v and 'service_account' in v:
        kind = 'service-account-json'
        try:
            obj = json.loads(v)
            email = obj.get('client_email','')
            extra = f'client_email={email}'
        except Exception:
            extra = 'json-parse-failed'
    # heuristic: path to file
    elif '\\' in v or '/' in v:
        p = Path(v)
        if p.exists():
            kind = 'file-path'
            try:
                extra = f'path_exists, size={p.stat().st_size} bytes'
                txt = p.read_text(2048)
                if txt.strip().startswith('{') and 'service_account' in txt:
                    kind = 'service-account-json-file'
                    extra = f'file_json, size={p.stat().st_size} bytes'
            except Exception as e:
                extra = 'file-read-error'
        else:
            kind = 'file-path-not-found'
    # heuristic: plausible API key (short token, common prefixes)
    elif len(v) > 10 and len(v) < 200 and all(c.isprintable() for c in v):
        kind = 'api-key-like'
        if v.startswith('AI') or v.startswith('AIza') or v.startswith('A-'):
            extra = 'starts-with-AI/AIza'
    elif len(v) > 200:
        kind = 'long-string'
    print(f"- {name}: preview='{preview}' kind={kind} {extra}")
# Also show .env first non-empty line masked if file exists in repo root
envpath = Path('.env')
if envpath.exists():
    try:
        text = envpath.read_text().splitlines()
        first = next((line for line in text if line.strip() and not line.strip().startswith('#')), None)
        if first:
            k,v = (first.split('=',1)+[''])[:2]
            pv = (v.strip()[:3] + '...') if len(v.strip())>3 else (v.strip()+'...')
            print(f"\n- .env first non-empty line: {k}='{pv}'")
        else:
            print('\n- .env: empty or no non-comment lines')
    except Exception as e:
        print(f"\n- .env: read error: {e}")
else:
    print('\n- .env: NOT FOUND in repository root')
