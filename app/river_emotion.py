import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import joblib
import os

class EmotionAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = SVC()
        self.emotions = ['happy', 'sad', 'anxious', 'peaceful', 'excited']
        
    def train(self, texts, labels):
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        
    def predict(self, text):
        X = self.vectorizer.transform([text])
        prediction = self.model.predict(X)[0]
        confidence = np.max(self.model.predict_proba(X))
        return {
            'emotion': prediction,
            'confidence': float(confidence)
        }

def analyze_emotion(text):
    """
    Analyze the emotional content of text related to rivers.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        dict: Analysis results including emotion and confidence
    """
    analyzer = EmotionAnalyzer()
    
    # Sample training data (in a real app, this would be loaded from a database)
    sample_texts = [
        "The river flows peacefully today",
        "I'm worried about the river's pollution",
        "The river makes me feel calm",
        "I'm excited to visit the river",
        "The river's condition makes me sad"
    ]
    sample_labels = ['peaceful', 'anxious', 'peaceful', 'excited', 'sad']
    
    analyzer.train(sample_texts, sample_labels)
    return analyzer.predict(text) 