from app.services.vocabulary_assessor import assessor

# Debug I'll
result = assessor.assess_sentence("I'll", 'B1')
for w in result['words']:
    print(f"Word: {w['word']}, Level: {w['level']}, is_beyond: {w['is_beyond']}")
    print(f"  Full dict: {w}")
