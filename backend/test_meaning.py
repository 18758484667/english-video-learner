import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.services.vocabulary_assessor import assessor

result = assessor.assess_sentence('The intricate phenomenon requires substantial', 'B1')
for w in result['words']:
    if w['is_beyond']:
        print(w['word'] + ': ' + str(w['meaning']))
