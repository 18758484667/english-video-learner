import urllib.request
import json

# 测试添加多个单词
words = ["specific", "hello", "world", "drumsticks"]
results = []

for word in words:
    # 先删除已存在的
    try:
        req = urllib.request.Request(f"http://localhost:8000/api/vocabulary/items/test_user")
        with urllib.request.urlopen(req, timeout=5) as response:
            items = json.loads(response.read().decode("utf-8"))
            for item in items:
                if item.get('word') == word:
                    delete_url = f"http://localhost:8000/api/vocabulary/items/{item['id']}"
                    req_del = urllib.request.Request(delete_url, method='DELETE')
                    with urllib.request.urlopen(req_del, timeout=5) as resp:
                        pass
                    break
    except:
        pass

    # 添加单词
    url = "http://localhost:8000/api/vocabulary/items/"
    headers = {"Content-Type": "application/json"}
    data = {
        "user_id": "test_user",
        "word": word,
        "source_video": "",
        "source_timestamp": 0
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
            results.append({
                "word": result.get('word'),
                "phonetic": result.get('phonetic'),
                "meaning": result.get('meaning'),
                "example": result.get('example_sentence')
            })
    except Exception as e:
        results.append({"word": word, "error": str(e)})

with open("test_multiple_results.txt", "w", encoding="utf-8") as f:
    for r in results:
        f.write(f"word: {r.get('word')}\n")
        f.write(f"  phonetic: {repr(r.get('phonetic'))}\n")
        f.write(f"  meaning: {repr(r.get('meaning'))}\n")
        f.write(f"  example: {repr(r.get('example'))}\n")
        f.write("\n")

print("done")
