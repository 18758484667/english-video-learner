import urllib.request
import json

# 测试 free dictionary API
words = ["drumsticks", "specific", "analysis", "hello"]

for word in words:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            with open(f"dict_api_{word}.txt", "w", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=2))
            print(f"{word}: success")
    except Exception as e:
        print(f"{word}: {e}")
