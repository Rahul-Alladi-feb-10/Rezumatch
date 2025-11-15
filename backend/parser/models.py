from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from django.conf import settings

# MongoDB Connection
try:
    client = MongoClient(
        settings.MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=45000,
        maxPoolSize=50
    )
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")
    raise

# Initialize database
db = client[settings.MONGO_DB_NAME]


class ResumeModel:
    """Model for storing parsed resumes"""
    collection = db['resumes']
    
    @staticmethod
    def create_resume(data):
        """
        Create a new resume entry
        
        :param data: Dictionary containing resume data
        :return: Inserted resume ID
        """
        resume_data = {
            "filename": data.get('filename'),
            "raw_text": data.get('raw_text'),
            "cleaned_text": data.get('cleaned_text'),
            "sections": data.get('sections', {}),  # Dict with keys: education, experience, skills, etc.
            "extracted_data": data.get('extracted_data', {}),  # Structured data
            "uploaded_at": datetime.utcnow(),
            "file_type": data.get('file_type'),  # pdf, docx
            "status": "parsed"
        }
        
        result = ResumeModel.collection.insert_one(resume_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_resume_by_id(resume_id):
        """Get resume by ID"""
        try:
            resume = ResumeModel.collection.find_one({"_id": ObjectId(resume_id)})
            if resume:
                resume['_id'] = str(resume['_id'])
            return resume
        except Exception as e:
            print(f"Error fetching resume: {e}")
            return None
    
    @staticmethod
    def get_all_resumes(limit=100):
        """Get all resumes"""
        resumes = list(ResumeModel.collection.find().sort("uploaded_at", -1).limit(limit))
        for resume in resumes:
            resume['_id'] = str(resume['_id'])
        return resumes
    
    @staticmethod
    def delete_resume(resume_id):
        """Delete a resume"""
        result = ResumeModel.collection.delete_one({"_id": ObjectId(resume_id)})
        return result.deleted_count


class JobDescriptionModel:
    """Model for storing parsed job descriptions"""
    collection = db['job_descriptions']
    
    @staticmethod
    def create_job(data):
        """
        Create a new job description entry
        
        :param data: Dictionary containing job description data
        :return: Inserted job ID
        """
        job_data = {
            "title": data.get('title'),
            "company": data.get('company'),
            "raw_text": data.get('raw_text'),
            "cleaned_text": data.get('cleaned_text'),
            "sections": data.get('sections', {}),
            "extracted_data": data.get('extracted_data', {}),
            "created_at": datetime.utcnow(),
            "status": "parsed"
        }
        
        result = JobDescriptionModel.collection.insert_one(job_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_job_by_id(job_id):
        """Get job description by ID"""
        try:
            job = JobDescriptionModel.collection.find_one({"_id": ObjectId(job_id)})
            if job:
                job['_id'] = str(job['_id'])
            return job
        except Exception as e:
            print(f"Error fetching job: {e}")
            return None
    
    @staticmethod
    def get_all_jobs(limit=100):
        """Get all job descriptions"""
        jobs = list(JobDescriptionModel.collection.find().sort("created_at", -1).limit(limit))
        for job in jobs:
            job['_id'] = str(job['_id'])
        return jobs
    
    @staticmethod
    def delete_job(job_id):
        """Delete a job description"""
        result = JobDescriptionModel.collection.delete_one({"_id": ObjectId(job_id)})
        return result.deleted_count


class MatchResultModel:
    """Model for storing match results between resumes and jobs"""
    collection = db['match_results']
    
    @staticmethod
    def create_match(resume_id, job_id, scores, details):
        """
        Create a match result
        
        :param resume_id: Resume ID
        :param job_id: Job description ID
        :param scores: Dictionary of score components
        :param details: Additional matching details
        :return: Inserted match ID
        """
        match_data = {
            "resume_id": resume_id,
            "job_id": job_id,
            "overall_score": scores.get('overall_score', 0),
            "keyword_score": scores.get('keyword_score', 0),
            "experience_score": scores.get('experience_score', 0),
            "semantic_score": scores.get('semantic_score', 0),
            "matching_skills": details.get('matching_skills', []),
            "missing_skills": details.get('missing_skills', []),
            "matched_at": datetime.utcnow()
        }
        
        result = MatchResultModel.collection.insert_one(match_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_matches_by_resume(resume_id, limit=10):
        """Get all matches for a resume"""
        matches = list(
            MatchResultModel.collection
            .find({"resume_id": resume_id})
            .sort("overall_score", -1)
            .limit(limit)
        )
        for match in matches:
            match['_id'] = str(match['_id'])
        return matches
    
    @staticmethod
    def get_matches_by_job(job_id, limit=10):
        """Get all matches for a job"""
        matches = list(
            MatchResultModel.collection
            .find({"job_id": job_id})
            .sort("overall_score", -1)
            .limit(limit)
        )
        for match in matches:
            match['_id'] = str(match['_id'])
        return matches