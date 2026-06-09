import urllib.request
import json

url = "http://localhost:8000/api/vocabulary/word-info/drumsticks"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))
        print(f"status: {data.get('level')}")
        print(f"phonetic: {data.get('phonetic')}")
        print(f"meaning: {data.get('meaning')}")
except Exception as e:
    print(f"error: {e}")
