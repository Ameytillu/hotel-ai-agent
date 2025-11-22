from model_loader import load_model_and_vectorizer
from utils.review_utils import clean_text

model, vectorizer = load_model_and_vectorizer()

def analyze_sentiment(review):
    cleaned = clean_text(review)
    vec = vectorizer.transform([cleaned])
    prediction = model.predict(vec)[0]
    return 'Positive' if prediction == 1 else 'Negative'

def respond_to_review(review):
    sentiment = analyze_sentiment(review)
    if sentiment == 'Negative':
        return "We’re sorry you had a bad experience. Our team will contact you shortly."
    else:
        return "Thank you for your kind words! We're happy you enjoyed your stay."