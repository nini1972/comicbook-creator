import requests
import sys

url = 'http://127.0.0.1:8002/generate-comic/?topic=Integration Test'
print(f"Requesting {url}")
with requests.get(url, stream=True) as r:
    try:
        for line in r.iter_lines(decode_unicode=True):
            if line:
                print(line)
                sys.stdout.flush()
    except Exception as e:
        print('Client exception:', e)
        raise
print('Client finished')
