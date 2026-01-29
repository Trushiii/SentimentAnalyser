from textblob import TextBlob
import pandas as pd
from collections import Counter
import re

class SentimentAnalyzer:
    """Analyzes sentiment of text using TextBlob"""
    
    def __init__(self):
        self.results = []

    
    def clean_text(self, text):
        """Clean text by removing URLs, mentions, hashtags symbols"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove mentions (@username)
        text = re.sub(r'@\w+', '', text)
        # Remove hashtag symbol but keep the word
        text = re.sub(r'#', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of a single text
        Returns: dict with text, sentiment, polarity, subjectivity
        """
        cleaned_text = self.clean_text(text)
        
        # Create TextBlob object (this is the AI part!)
        blob = TextBlob(cleaned_text)
        
        # Get polarity (-1 to 1) and subjectivity (0 to 1)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classify sentiment based on polarity
        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        return {
            'text': text,
            'cleaned_text': cleaned_text,
            'sentiment': sentiment,
            'polarity': round(polarity, 3),
            'subjectivity': round(subjectivity, 3)
        }
    
    def analyze_multiple(self, texts):
        """Analyze multiple texts and return results"""
        self.results = []
        
        for text in texts:
            if text.strip():  # Skip empty texts
                result = self.analyze_sentiment(text)
                self.results.append(result)
        
        return self.results
    
    def get_statistics(self):
        """Calculate statistics from analyzed results"""
        if not self.results:
            return None
        
        df = pd.DataFrame(self.results)
        
        # Count sentiments
        sentiment_counts = df['sentiment'].value_counts()
        total = len(df)
        
        stats = {
            'total': total,
            'positive': sentiment_counts.get('Positive', 0),
            'negative': sentiment_counts.get('Negative', 0),
            'neutral': sentiment_counts.get('Neutral', 0),
            'positive_pct': round((sentiment_counts.get('Positive', 0) / total) * 100, 1),
            'negative_pct': round((sentiment_counts.get('Negative', 0) / total) * 100, 1),
            'neutral_pct': round((sentiment_counts.get('Neutral', 0) / total) * 100, 1),
            'avg_polarity': round(df['polarity'].mean(), 3),
            'avg_subjectivity': round(df['subjectivity'].mean(), 3)
        }
        
        return stats
    
    def get_top_words(self, sentiment_type=None, top_n=10):
        """Get most common words for a specific sentiment type"""
        if not self.results:
            return []
        
        df = pd.DataFrame(self.results)
        
        # Filter by sentiment if specified
        if sentiment_type:
            df = df[df['sentiment'] == sentiment_type]
        
        # Combine all cleaned texts
        all_text = ' '.join(df['cleaned_text'].tolist())
        
        # Remove common words (stopwords)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                    'of', 'with', 'is', 'was', 'are', 'been', 'be', 'have', 'has', 'had',
                    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those'}
        
        # Split into words and count
        words = [word.lower() for word in all_text.split() 
                 if len(word) > 2 and word.lower() not in stopwords]
        
        # Get top words
        word_counts = Counter(words).most_common(top_n)
        
        return word_counts 