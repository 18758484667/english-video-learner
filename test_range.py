import urllib.request

# 测试 Range 请求
req = urllib.request.Request("http://localhost:8000/api/videos/file/1")
req.add_header("Range", "bytes=0-10")

try:
    with urllib.request.urlopen(req, timeout=5) as response:
        print(f"Status: {response.status}")
        print(f"Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        data = response.read()
        print(f"Body length: {len(data)}")
except Exception as e:
    print(f"Error: {e}")
