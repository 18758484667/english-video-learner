import urllib.request
import json

# 先删除已存在的 drumsticks
# 获取用户的生词列表
url = "http://localhost:8000/api/vocabulary/items/test_user"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        items = json.loads(response.read().decode("utf-8"))
        print(f"Found {len(items)} items")
        for item in items:
            if item.get('word') == 'drumsticks':
                delete_url = f"http://localhost:8000/api/vocabulary/items/{item['id']}"
                req_del = urllib.request.Request(delete_url, method='DELETE')
                with urllib.request.urlopen(req_del, timeout=5) as resp:
                    print(f"Deleted drumsticks (id={item['id']})")
                break
        else:
            print("drumsticks not found in vocabulary")
except Exception as e:
    print(f"error: {e}")
