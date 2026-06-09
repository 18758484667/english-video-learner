from app.database import SessionLocal
from app.models import VocabularyLevel

session = SessionLocal()
words = ["do", "not", "will", "would", "could", "should", "can", "have", "has", "had", "i", "you", "we", "they", "he", "she", "it", "am", "are", "is", "let", "us"]
for w in words:
    vocab = session.query(VocabularyLevel).filter(VocabularyLevel.word == w).first()
    if vocab:
        print(f'{w}: {vocab.level}')
    else:
        print(f'{w}: NOT FOUND')
