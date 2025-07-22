import joblib

def load_model_and_vectorizer():
    model = joblib.load('model/sentiment_model.pkl')
    vectorizer = joblib.load('model/tfidf_vectorizer.pkl')
    return model, vectorizer