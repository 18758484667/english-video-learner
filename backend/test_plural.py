from app.services.vocabulary_assessor import assessor

result = assessor.assess_sentence('chefs and artists have knives', 'B1')
for w in result['words']:
    print(w['word'] + ': level=' + w['level'] + ', is_beyond=' + str(w['is_beyond']))
