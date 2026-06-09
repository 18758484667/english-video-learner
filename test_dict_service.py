import sys
sys.path.insert(0, "backend/app/services")

from translator import DictionaryService

dict_service = DictionaryService()

for word in ["drumsticks", "drumstick", "specific"]:
    print(f"\n=== Testing {word} ===")
    result = dict_service.get_word_info(word)
    if result:
        print(f"phonetic: {repr(result.get('phonetic'))}")
        print(f"definitions: {result.get('definitions')}")
    else:
        print("No result")
