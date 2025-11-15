# parser/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ResumeModel, JobDescriptionModel, MatchResultModel
from .utils.file_parser import DocumentParser
from .utils.text_cleaner import TextCleaner
from .utils.section_extractor import SectionExtractor
from .utils.matcher import ResumeJobMatcher


@api_view(['POST'])
def upload_resume(request):
    """
    Upload and parse a resume file
    
    Expected: Multipart form data with 'file' field
    """
    try:
        # Check if file is present
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_obj = request.FILES['file']
        filename = file_obj.name
        
        # Parse document
        raw_text, file_type = DocumentParser.parse_document(file_obj, filename)
        
        # Clean text - normalize whitespace first
        cleaner = TextCleaner()
        normalized_text = cleaner.normalize_whitespace(raw_text)
        
        # Extract sections first (for context-aware extraction)
        extractor = SectionExtractor()
        sections = extractor.extract_sections(normalized_text)
        
        # Extract structured data with section context
        extracted_data = {
            'skills': extractor.extract_skills(normalized_text, sections),
            'education': extractor.extract_education(normalized_text, sections),
            'experience': extractor.extract_experience(normalized_text, sections),
            'contact': extractor.extract_contact_info(normalized_text),
        }
        
        # Clean text for vectorization (done after extraction to preserve structure)
        cleaned_text = cleaner.full_preprocessing(normalized_text)
        extracted_data['keywords'] = cleaner.extract_keywords(cleaned_text)
        
        # Save to database
        resume_id = ResumeModel.create_resume({
            'filename': filename,
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'sections': sections,
            'extracted_data': extracted_data,
            'file_type': file_type
        })
        
        return Response({
            'message': 'Resume uploaded and parsed successfully',
            'resume_id': resume_id,
            'data': {
                'filename': filename,
                'file_type': file_type,
                'sections_found': list(sections.keys()),
                'skills_extracted': extracted_data['skills'],
                'skills_count': len(extracted_data['skills']),
                'education_count': len(extracted_data['education']),
                'experience_count': len(extracted_data['experience']),
                'contact_info': extracted_data['contact'],
                'keywords': extracted_data['keywords'][:10]  # Top 10 keywords
            }
        }, status=status.HTTP_201_CREATED)
    
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================
# MATCHING ENDPOINTS (Step 2)
# ============================================

@api_view(['POST'])
def match_resume_to_job(request):
    """
    Match a single resume to a single job description
    
    Expected JSON: {
        "resume_id": "...",
        "job_id": "..."
    }
    """
    try:
        resume_id = request.data.get('resume_id')
        job_id = request.data.get('job_id')
        
        if not resume_id or not job_id:
            return Response(
                {'error': 'Both resume_id and job_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Fetch resume and job
        resume = ResumeModel.get_resume_by_id(resume_id)
        job = JobDescriptionModel.get_job_by_id(job_id)
        
        if not resume:
            return Response(
                {'error': 'Resume not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not job:
            return Response(
                {'error': 'Job description not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Perform matching
        matcher = ResumeJobMatcher()
        match_result = matcher.match(resume, job)
        
        # Save match result to database
        match_id = MatchResultModel.create_match(
            resume_id=resume_id,
            job_id=job_id,
            scores={
                'overall_score': match_result['overall_score'],
                'keyword_score': match_result['component_scores']['keyword_match'],
                'semantic_score': match_result['component_scores']['semantic_match'],
                'experience_score': match_result['component_scores']['experience_match']
            },
            details={
                'matching_skills': match_result['skills_details']['matching_skills'],
                'missing_skills': match_result['skills_details']['missing_skills'],
                'fuzzy_matches': match_result['skills_details'].get('fuzzy_matches', []),
                'match_quality': match_result['match_quality']
            }
        )
        
        return Response({
            'message': 'Matching completed successfully',
            'match_id': match_id,
            'result': match_result
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def match_resume_to_all_jobs(request):
    """
    Match a single resume to all job descriptions
    
    Expected JSON: {
        "resume_id": "..."
    }
    """
    try:
        resume_id = request.data.get('resume_id')
        
        if not resume_id:
            return Response(
                {'error': 'resume_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Fetch resume
        resume = ResumeModel.get_resume_by_id(resume_id)
        
        if not resume:
            return Response(
                {'error': 'Resume not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Fetch all jobs
        jobs = JobDescriptionModel.get_all_jobs()
        
        if not jobs:
            return Response(
                {'error': 'No job descriptions found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Perform batch matching
        matcher = ResumeJobMatcher()
        results = matcher.batch_match(resume, jobs)
        
        # Save top matches to database
        for result in results[:10]:  # Save top 10 matches
            MatchResultModel.create_match(
                resume_id=resume_id,
                job_id=result['job_id'],
                scores={
                    'overall_score': result['overall_score'],
                    'keyword_score': result['component_scores']['keyword_match'],
                    'semantic_score': result['component_scores']['semantic_match'],
                    'experience_score': result['component_scores']['experience_match']
                },
                details={
                    'matching_skills': result['skills_details']['matching_skills'],
                    'missing_skills': result['skills_details']['missing_skills'],
                    'match_quality': result['match_quality']
                }
            )
        
        return Response({
            'message': 'Batch matching completed successfully',
            'total_jobs_matched': len(results),
            'results': results
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def match_job_to_all_resumes(request):
    """
    Match a single job to all resumes (for recruiters)
    
    Expected JSON: {
        "job_id": "..."
    }
    """
    try:
        job_id = request.data.get('job_id')
        
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Fetch job
        job = JobDescriptionModel.get_job_by_id(job_id)
        
        if not job:
            return Response(
                {'error': 'Job description not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Fetch all resumes
        resumes = ResumeModel.get_all_resumes()
        
        if not resumes:
            return Response(
                {'error': 'No resumes found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Perform batch matching
        matcher = ResumeJobMatcher()
        results = matcher.batch_match_resumes(resumes, job)
        
        # Save all matches to database
        for result in results:
            MatchResultModel.create_match(
                resume_id=result['resume_id'],
                job_id=job_id,
                scores={
                    'overall_score': result['overall_score'],
                    'keyword_score': result['component_scores']['keyword_match'],
                    'semantic_score': result['component_scores']['semantic_match'],
                    'experience_score': result['component_scores']['experience_match']
                },
                details={
                    'matching_skills': result['skills_details']['matching_skills'],
                    'missing_skills': result['skills_details']['missing_skills'],
                    'match_quality': result['match_quality']
                }
            )
        
        return Response({
            'message': 'Batch matching completed successfully',
            'total_resumes_matched': len(results),
            'results': results
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def upload_job_description(request):
    """
    Upload and parse a job description
    
    Expected: JSON with 'title', 'company', and 'description' fields
    OR Multipart form data with 'file' field
    """
    try:
        # Check if it's a file upload or text input
        if 'file' in request.FILES:
            # Parse from file
            file_obj = request.FILES['file']
            filename = file_obj.name
            raw_text, file_type = DocumentParser.parse_document(file_obj, filename)
            title = request.data.get('title', 'Unknown Position')
            company = request.data.get('company', 'Unknown Company')
        
        elif 'description' in request.data:
            # Parse from text input
            raw_text = request.data.get('description')
            title = request.data.get('title', 'Unknown Position')
            company = request.data.get('company', 'Unknown Company')
        
        else:
            return Response(
                {'error': 'No job description provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Clean text
        cleaner = TextCleaner()
        normalized_text = cleaner.normalize_whitespace(raw_text)
        
        # Extract sections
        extractor = SectionExtractor()
        sections = extractor.extract_sections(normalized_text)
        
        # Extract structured data
        extracted_data = {
            'required_skills': extractor.extract_skills(normalized_text, sections),
        }
        
        # Clean for vectorization
        cleaned_text = cleaner.full_preprocessing(normalized_text)
        extracted_data['keywords'] = cleaner.extract_keywords(cleaned_text)
        
        # Save to database
        job_id = JobDescriptionModel.create_job({
            'title': title,
            'company': company,
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'sections': sections,
            'extracted_data': extracted_data
        })
        
        return Response({
            'message': 'Job description uploaded and parsed successfully',
            'job_id': job_id,
            'data': {
                'title': title,
                'company': company,
                'sections_found': list(sections.keys()),
                'required_skills': extracted_data['required_skills']
            }
        }, status=status.HTTP_201_CREATED)
    
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_resume(request, resume_id):
    """Get a specific resume by ID"""
    try:
        resume = ResumeModel.get_resume_by_id(resume_id)
        
        if not resume:
            return Response(
                {'error': 'Resume not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(resume, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_all_resumes(request):
    """Get all resumes"""
    try:
        resumes = ResumeModel.get_all_resumes()
        return Response({
            'count': len(resumes),
            'resumes': resumes
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_job(request, job_id):
    """Get a specific job description by ID"""
    try:
        job = JobDescriptionModel.get_job_by_id(job_id)
        
        if not job:
            return Response(
                {'error': 'Job description not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(job, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_all_jobs(request):
    """Get all job descriptions"""
    try:
        jobs = JobDescriptionModel.get_all_jobs()
        return Response({
            'count': len(jobs),
            'jobs': jobs
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def delete_resume(request, resume_id):
    """Delete a resume"""
    try:
        deleted_count = ResumeModel.delete_resume(resume_id)
        
        if deleted_count == 0:
            return Response(
                {'error': 'Resume not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {'message': 'Resume deleted successfully'},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def delete_job(request, job_id):
    """Delete a job description"""
    try:
        deleted_count = JobDescriptionModel.delete_job(job_id)
        
        if deleted_count == 0:
            return Response(
                {'error': 'Job description not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {'message': 'Job description deleted successfully'},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )