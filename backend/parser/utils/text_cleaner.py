# parser/utils/text_cleaner.py

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')


class TextCleaner:
    """Clean and preprocess text for NLP tasks"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def normalize_whitespace(self, text):
        """
        Normalize excessive whitespace and newlines
        
        :param text: Input text
        :return: Normalized text
        """
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Remove spaces before newlines
        text = re.sub(r' +\n', '\n', text)
        
        # Remove trailing/leading whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def clean_text(self, text, preserve_case=False):
        """
        Clean and preprocess text
        
        :param text: Input text string
        :param preserve_case: Whether to preserve case (useful for NER)
        :return: Cleaned text
        """
        # First normalize whitespace
        text = self.normalize_whitespace(text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses (but save them separately if needed)
        # text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\.\,\-\(\)\+\@]', ' ', text)
        
        # Remove multiple spaces again after cleaning
        text = re.sub(r' +', ' ', text)
        
        # Convert to lowercase if not preserving case
        if not preserve_case:
            text = text.lower()
        
        return text.strip()
    
    def remove_stopwords(self, text):
        """
        Remove stopwords from text
        
        :param text: Input text string
        :return: Text without stopwords
        """
        words = word_tokenize(text)
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        return ' '.join(filtered_words)
    
    def lemmatize_text(self, text):
        """
        Lemmatize text (reduce words to base form)
        
        :param text: Input text string
        :return: Lemmatized text
        """
        words = word_tokenize(text)
        lemmatized_words = [self.lemmatizer.lemmatize(word) for word in words]
        return ' '.join(lemmatized_words)
    
    def full_preprocessing(self, text, remove_stops=True, lemmatize=True):
        """
        Complete preprocessing pipeline
        
        :param text: Input text string
        :param remove_stops: Whether to remove stopwords
        :param lemmatize: Whether to lemmatize
        :return: Fully preprocessed text
        """
        # Clean text
        cleaned = self.clean_text(text)
        
        # Remove stopwords if requested
        if remove_stops:
            cleaned = self.remove_stopwords(cleaned)
        
        # Lemmatize if requested
        if lemmatize:
            cleaned = self.lemmatize_text(cleaned)
        
        return cleaned
    
    def extract_keywords(self, text, top_n=20):
        """
        Extract important keywords from text
        
        :param text: Input text string
        :param top_n: Number of top keywords to extract
        :return: List of keywords
        """
        # Clean and tokenize
        cleaned = self.clean_text(text, preserve_case=False)
        words = word_tokenize(cleaned)
        
        # Remove stopwords and short words
        keywords = [
            word for word in words 
            if word.lower() not in self.stop_words and len(word) > 2
        ]
        
        # Count frequency
        from collections import Counter
        word_freq = Counter(keywords)
        
        # Return top N keywords
        return [word for word, count in word_freq.most_common(top_n)]