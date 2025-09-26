import requests

# Test the health endpoint of the Comic Book Creator API
url = "http://127.0.0.1:8002/"
try:
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error connecting to API: {e}")
