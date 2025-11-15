# parser/utils/vectorizer.py

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import pickle
import os


class ResumeVectorizer:
    """Vectorize resumes and job descriptions for matching"""
    
    def __init__(self):
        # Initialize TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),  # Unigrams and bigrams
            stop_words='english',
            lowercase=True
        )
        
        # Initialize Sentence-BERT model (lightweight model)
        print("Loading Sentence-BERT model...")
        self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence-BERT model loaded")
        
        self.is_tfidf_fitted = False
    
    def vectorize_tfidf(self, texts, fit=False):
        """
        Vectorize texts using TF-IDF
        
        :param texts: List of text strings or single text
        :param fit: Whether to fit the vectorizer (True for first time)
        :return: TF-IDF vectors (numpy array or sparse matrix)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        if fit or not self.is_tfidf_fitted:
            # Fit and transform
            vectors = self.tfidf_vectorizer.fit_transform(texts)
            self.is_tfidf_fitted = True
        else:
            # Only transform
            vectors = self.tfidf_vectorizer.transform(texts)
        
        return vectors
    
    def vectorize_sbert(self, texts):
        """
        Vectorize texts using Sentence-BERT
        
        :param texts: List of text strings or single text
        :return: SBERT embeddings (numpy array)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # Generate embeddings
        embeddings = self.sbert_model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def compute_similarity(self, vector1, vector2, method='cosine'):
        """
        Compute similarity between two vectors
        
        :param vector1: First vector
        :param vector2: Second vector
        :param method: Similarity method (default: cosine)
        :return: Similarity score (0 to 1)
        """
        if method == 'cosine':
            # Handle both sparse and dense matrices
            similarity = cosine_similarity(vector1, vector2)
            return float(similarity[0][0])
        else:
            raise ValueError(f"Unknown similarity method: {method}")
    
    def hybrid_vectorize(self, text, fit_tfidf=False):
        """
        Create hybrid representation using both TF-IDF and SBERT
        
        :param text: Text to vectorize
        :param fit_tfidf: Whether to fit TF-IDF vectorizer
        :return: Dictionary with both vector types
        """
        return {
            'tfidf': self.vectorize_tfidf(text, fit=fit_tfidf),
            'sbert': self.vectorize_sbert(text)
        }
    
    def save_tfidf_vectorizer(self, filepath):
        """Save fitted TF-IDF vectorizer"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.tfidf_vectorizer, f)
    
    def load_tfidf_vectorizer(self, filepath):
        """Load fitted TF-IDF vectorizer"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                self.tfidf_vectorizer = pickle.load(f)
                self.is_tfidf_fitted = True
            return True
        return False


class SkillMatcher:
    """Match skills between resume and job description"""
    
    @staticmethod
    def exact_match(resume_skills, job_skills):
        """
        Find exact skill matches
        
        :param resume_skills: List of skills from resume
        :param job_skills: List of required skills from job
        :return: Dictionary with matching and missing skills
        """
        # Normalize skills to lowercase for comparison
        resume_skills_lower = {skill.lower() for skill in resume_skills}
        job_skills_lower = {skill.lower() for skill in job_skills}
        
        # Find matches
        matching_skills = resume_skills_lower.intersection(job_skills_lower)
        missing_skills = job_skills_lower - resume_skills_lower
        
        # Get original case for display
        matching_display = [skill for skill in job_skills if skill.lower() in matching_skills]
        missing_display = [skill for skill in job_skills if skill.lower() in missing_skills]
        
        return {
            'matching_skills': matching_display,
            'missing_skills': missing_display,
            'match_count': len(matching_skills),
            'total_required': len(job_skills_lower),
            'match_percentage': (len(matching_skills) / len(job_skills_lower) * 100) if job_skills_lower else 0
        }
    
    @staticmethod
    def fuzzy_match(resume_skills, job_skills, threshold=0.8):
        """
        Find fuzzy skill matches (similar but not exact)
        
        :param resume_skills: List of skills from resume
        :param job_skills: List of required skills from job
        :param threshold: Similarity threshold (0 to 1)
        :return: Dictionary with fuzzy matches
        """
        from difflib import SequenceMatcher
        
        fuzzy_matches = []
        
        for job_skill in job_skills:
            best_match = None
            best_ratio = 0
            
            for resume_skill in resume_skills:
                ratio = SequenceMatcher(None, job_skill.lower(), resume_skill.lower()).ratio()
                if ratio > best_ratio and ratio >= threshold:
                    best_ratio = ratio
                    best_match = resume_skill
            
            if best_match:
                fuzzy_matches.append({
                    'required': job_skill,
                    'found': best_match,
                    'similarity': round(best_ratio * 100, 2)
                })
        
        return {
            'fuzzy_matches': fuzzy_matches,
            'fuzzy_match_count': len(fuzzy_matches)
        }


class ExperienceMatcher:
    """Match experience levels and duration"""
    
    @staticmethod
    def extract_years_from_text(text):
        """
        Extract years of experience from text
        
        :param text: Text containing experience info
        :return: Number of years (float)
        """
        import re
        
        # Patterns for "X years" or "X+ years"
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return float(match.group(1))
        
        return 0.0
    
    @staticmethod
    def calculate_experience_from_dates(experiences):
        """
        Calculate total years of experience from experience entries
        
        :param experiences: List of experience strings with dates
        :return: Total years of experience
        """
        import re
        from datetime import datetime
        
        total_months = 0
        
        month_map = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
            'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
            'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
            'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
            'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        
        for exp in experiences:
            exp_lower = exp.lower()
            
            # Try to find date range
            date_pattern = r'(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{4})\s*[-–—]\s*(?:(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{4})|(present|current))'
            
            match = re.search(date_pattern, exp_lower)
            if match:
                start_month_str = match.group(1)[:3]
                start_year = int(match.group(2))
                
                # Get start month number
                start_month = month_map.get(start_month_str, 1)
                
                # Calculate end date
                if match.group(5):  # present/current
                    end_year = datetime.now().year
                    end_month = datetime.now().month
                else:
                    end_month_str = match.group(3)[:3] if match.group(3) else 'dec'
                    end_year = int(match.group(4)) if match.group(4) else start_year
                    end_month = month_map.get(end_month_str, 12)
                
                # Calculate months
                months = (end_year - start_year) * 12 + (end_month - start_month)
                total_months += max(months, 0)
        
        return round(total_months / 12, 1)
    
    @staticmethod
    def match_experience(resume_years, required_years):
        """
        Calculate experience match score
        
        :param resume_years: Years of experience in resume
        :param required_years: Required years of experience
        :return: Match score and details
        """
        if required_years == 0:
            return {
                'score': 100,
                'resume_years': resume_years,
                'required_years': required_years,
                'meets_requirement': True
            }
        
        # Calculate score
        if resume_years >= required_years:
            score = 100
            meets_requirement = True
        else:
            # Partial credit if close
            score = (resume_years / required_years) * 100
            meets_requirement = False
        
        return {
            'score': round(score, 2),
            'resume_years': resume_years,
            'required_years': required_years,
            'meets_requirement': meets_requirement
        }