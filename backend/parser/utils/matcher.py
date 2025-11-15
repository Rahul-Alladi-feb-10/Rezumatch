# parser/utils/matcher.py

from .vectorizer import ResumeVectorizer, SkillMatcher, ExperienceMatcher
import numpy as np


class ResumeJobMatcher:
    """Main matching engine for resume-job matching"""
    
    def __init__(self):
        self.vectorizer = ResumeVectorizer()
        self.skill_matcher = SkillMatcher()
        self.experience_matcher = ExperienceMatcher()
    
    def match(self, resume_data, job_data, weights=None):
        """
        Comprehensive matching between resume and job description
        
        :param resume_data: Dictionary with resume data (from MongoDB)
        :param job_data: Dictionary with job data (from MongoDB)
        :param weights: Dictionary with component weights (optional)
        :return: Match result with scores and details
        """
        if weights is None:
            weights = {
                'keyword': 0.25,      # 25% - Exact keyword matching (TF-IDF)
                'semantic': 0.35,     # 35% - Semantic similarity (SBERT)
                'skills': 0.30,       # 30% - Skills matching
                'experience': 0.10    # 10% - Experience matching
            }
        
        # Extract texts
        resume_text = resume_data.get('cleaned_text', '')
        job_text = job_data.get('cleaned_text', '')
        
        # 1. Keyword Matching (TF-IDF)
        keyword_score = self._calculate_keyword_match(resume_text, job_text)
        
        # 2. Semantic Matching (SBERT)
        semantic_score = self._calculate_semantic_match(resume_text, job_text)
        
        # 3. Skills Matching
        resume_skills = resume_data.get('extracted_data', {}).get('skills', [])
        job_skills = job_data.get('extracted_data', {}).get('required_skills', [])
        skills_result = self._calculate_skills_match(resume_skills, job_skills)
        
        # 4. Experience Matching
        resume_experience = resume_data.get('extracted_data', {}).get('experience', [])
        experience_score = self._calculate_experience_match(
            resume_text,
            job_text,
            resume_experience
        )
        
        # Calculate weighted overall score
        overall_score = (
            keyword_score * weights['keyword'] +
            semantic_score * weights['semantic'] +
            skills_result['score'] * weights['skills'] +
            experience_score * weights['experience']
        )
        
        # Compile results
        result = {
            'overall_score': round(overall_score, 2),
            'component_scores': {
                'keyword_match': round(keyword_score, 2),
                'semantic_match': round(semantic_score, 2),
                'skills_match': round(skills_result['score'], 2),
                'experience_match': round(experience_score, 2)
            },
            'skills_details': skills_result['details'],
            'match_quality': self._get_match_quality(overall_score),
            'weights_used': weights
        }
        
        return result
    
    def _calculate_keyword_match(self, resume_text, job_text):
        """Calculate TF-IDF based keyword matching"""
        try:
            # Vectorize both texts
            vectors = self.vectorizer.vectorize_tfidf([resume_text, job_text], fit=True)
            
            # Calculate cosine similarity
            similarity = self.vectorizer.compute_similarity(
                vectors[0:1],  # Resume vector
                vectors[1:2]   # Job vector
            )
            
            return similarity * 100  # Convert to percentage
        except Exception as e:
            print(f"Error in keyword matching: {e}")
            return 0.0
    
    def _calculate_semantic_match(self, resume_text, job_text):
        """Calculate Sentence-BERT based semantic matching"""
        try:
            # Generate embeddings
            embeddings = self.vectorizer.vectorize_sbert([resume_text, job_text])
            
            # Calculate cosine similarity
            similarity = self.vectorizer.compute_similarity(
                embeddings[0:1].reshape(1, -1),
                embeddings[1:2].reshape(1, -1)
            )
            
            return similarity * 100  # Convert to percentage
        except Exception as e:
            print(f"Error in semantic matching: {e}")
            return 0.0
    
    def _calculate_skills_match(self, resume_skills, job_skills):
        """Calculate skills matching score"""
        if not job_skills:
            return {'score': 100, 'details': {'matching_skills': [], 'missing_skills': []}}
        
        # Exact matching
        exact_match = self.skill_matcher.exact_match(resume_skills, job_skills)
        
        # Fuzzy matching for missing skills
        fuzzy_result = self.skill_matcher.fuzzy_match(
            resume_skills,
            exact_match['missing_skills'],
            threshold=0.75
        )
        
        # Calculate final score
        total_matched = exact_match['match_count'] + fuzzy_result['fuzzy_match_count']
        total_required = exact_match['total_required']
        
        if total_required > 0:
            score = (total_matched / total_required) * 100
        else:
            score = 100
        
        return {
            'score': score,
            'details': {
                'matching_skills': exact_match['matching_skills'],
                'missing_skills': exact_match['missing_skills'],
                'fuzzy_matches': fuzzy_result.get('fuzzy_matches', []),
                'match_count': total_matched,
                'total_required': total_required
            }
        }
    
    def _calculate_experience_match(self, resume_text, job_text, resume_experiences):
        """Calculate experience matching score"""
        try:
            # Extract required years from job description
            required_years = self.experience_matcher.extract_years_from_text(job_text)
            
            # Calculate resume years from experience entries
            resume_years = self.experience_matcher.calculate_experience_from_dates(
                resume_experiences
            )
            
            # If no specific requirement, give full score
            if required_years == 0:
                return 100
            
            # Calculate match
            exp_match = self.experience_matcher.match_experience(resume_years, required_years)
            
            return exp_match['score']
        except Exception as e:
            print(f"Error in experience matching: {e}")
            return 50  # Neutral score on error
    
    def _get_match_quality(self, score):
        """Get qualitative match rating"""
        if score >= 80:
            return 'Excellent Match'
        elif score >= 65:
            return 'Good Match'
        elif score >= 50:
            return 'Fair Match'
        elif score >= 35:
            return 'Poor Match'
        else:
            return 'Not a Match'
    
    def batch_match(self, resume_data, job_list):
        """
        Match one resume against multiple jobs
        
        :param resume_data: Single resume data
        :param job_list: List of job descriptions
        :return: List of match results sorted by score
        """
        results = []
        
        for job_data in job_list:
            match_result = self.match(resume_data, job_data)
            match_result['job_id'] = job_data.get('_id')
            match_result['job_title'] = job_data.get('title')
            match_result['company'] = job_data.get('company')
            results.append(match_result)
        
        # Sort by overall score (descending)
        results.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return results
    
    def batch_match_resumes(self, resume_list, job_data):
        """
        Match multiple resumes against one job
        
        :param resume_list: List of resumes
        :param job_data: Single job description
        :return: List of match results sorted by score
        """
        results = []
        
        for resume_data in resume_list:
            match_result = self.match(resume_data, job_data)
            match_result['resume_id'] = resume_data.get('_id')
            match_result['filename'] = resume_data.get('filename')
            results.append(match_result)
        
        # Sort by overall score (descending)
        results.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return results