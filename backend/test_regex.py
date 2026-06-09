import re

sentence = "I've been working and it's going well."

# 测试新正则
pattern = r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b"
words = re.findall(pattern, sentence)
print("Result:", words)
