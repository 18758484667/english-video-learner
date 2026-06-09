import urllib.request
import json

# 测试 API 返回的数据
url = "http://localhost:8000/api/vocabulary/word-info/specific"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode('utf-8'))
        with open("api_test.txt", "w", encoding="utf-8") as f:
            f.write(f"phonetic repr={repr(data.get('phonetic'))}\n")
            f.write(f"meaning repr={repr(data.get('meaning'))}\n")
            f.write(f"phonetic={data.get('phonetic')}\n")
            f.write(f"meaning={data.get('meaning')}\n")
        print("done")
except Exception as e:
    print(f"error: {e}")
