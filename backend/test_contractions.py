from app.database import SessionLocal
from app.models import VocabularyLevel

session = SessionLocal()
words = ["don't", "won't", "can't", "isn't", "aren't", "i'm", "you're", "we're", "they're", "i'll", "you'll", "we'll", "i've", "you've", "we've", "i'd", "you'd", "let's", "it's", "that's", "he's", "she's", "wouldn't", "shouldn't", "couldn't", "didn't", "doesn't", "haven't", "hasn't", "hadn't"]
for w in words:
    vocab = session.query(VocabularyLevel).filter(VocabularyLevel.word == w).first()
    if vocab:
        print(f'{w}: {vocab.level}')
    else:
        print(f'{w}: NOT FOUND')
