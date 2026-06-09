from app.database import SessionLocal
from app.models import VocabularyLevel

session = SessionLocal()
words = ['ill', 'll', 'i', 'will', 'ill']
for w in words:
    vocab = session.query(VocabularyLevel).filter(VocabularyLevel.word == w).first()
    if vocab:
        print(f'{w}: {vocab.level}')
    else:
        print(f'{w}: NOT FOUND')
