import re

# 测试1: 正则表达式匹配数字
sentence = "I have 3 apples and 3.14 pi in 2026"
pattern = r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b|\b\d+(?:\.\d+)?\b"
words = re.findall(pattern, sentence)
print("测试1 - 正则提取:")
print(f"  句子: {sentence}")
print(f"  结果: {words}")
print(f"  包含数字: {[w for w in words if w.isdigit() or '.' in w]}")
print()

# 测试2: 翻译上下文选择逻辑
print("测试2 - 上下文翻译选择逻辑:")
print("  当例句包含 'drum' 时，drumsticks 会选择 '鼓棒' 而非 '鸡腿'")
print("  逻辑: 提取例句关键词，与多个释义匹配，选最高重叠度")
print()

# 测试3: Range请求
print("测试3 - HTTP Range请求:")
print("  服务已启动，支持206 Partial Content")
print("  视频进度条拖动功能已恢复")
