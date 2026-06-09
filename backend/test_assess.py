from app.services.vocabulary_assessor import assessor

sentence = "I've been working and it's going well."
result = assessor.assess_sentence(sentence, 'A2')

for w in result['words']:
    print(f"{w['word']} (level={w['level']}, beyond={w['is_beyond']})")
