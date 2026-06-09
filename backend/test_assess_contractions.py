from app.services.vocabulary_assessor import assessor

sentences = [
    "I don't like this",
    "we're not going",
    "I'll get it",
    "I've done it",
    "let's go",
    "you can't help",
    "it won't work",
    "they've finished",
]

for s in sentences:
    result = assessor.assess_sentence(s, 'B1')
    print(f'Sentence: {s}')
    for w in result['words']:
        print(f"  {w['word']}: level={w['level']}, is_beyond={w['is_beyond']}")
    print()
