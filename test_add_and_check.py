import urllib.request
import json

# 删除已存在的 drumsticks
url = "http://localhost:8000/api/vocabulary/items/test_user"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        items = json.loads(response.read().decode("utf-8"))
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

# 添加 drumsticks
url = "http://localhost:8000/api/vocabulary/items/"
headers = {"Content-Type": "application/json"}
data = {
    "user_id": "test_user",
    "word": "drumsticks",
    "source_video": "",
    "source_timestamp": 0
}

try:
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        result = json.loads(response.read().decode("utf-8"))
        with open("test_add_word_result.txt", "w", encoding="utf-8") as f:
            f.write(f"word: {result.get('word')}\n")
            f.write(f"phonetic: {repr(result.get('phonetic'))}\n")
            f.write(f"meaning: {repr(result.get('meaning'))}\n")
            f.write(f"cefr_level: {result.get('cefr_level')}\n")
            f.write(f"example_sentence: {repr(result.get('example_sentence'))}\n")
        print("done")
except Exception as e:
    print(f"error: {e}")
    import traceback
    traceback.print_exc()
