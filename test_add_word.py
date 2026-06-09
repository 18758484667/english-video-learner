import urllib.request
import json

# 测试添加生词 - drumsticks
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
