# parser/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ResumeModel, JobDescriptionModel
from .utils.file_parser import DocumentParser
from .utils.text_cleaner import TextCleaner
from .utils.section_extractor import SectionExtractor


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
        
        # Clean text
        cleaner = TextCleaner()
        cleaned_text = cleaner.full_preprocessing(raw_text)
        
        # Extract sections
        extractor = SectionExtractor()
        sections = extractor.extract_sections(raw_text)
        
        # Extract structured data
        extracted_data = {
            'skills': extractor.extract_skills(raw_text),
            'education': extractor.extract_education(raw_text),
            'experience': extractor.extract_experience(raw_text),
            'contact': extractor.extract_contact_info(raw_text),
            'keywords': cleaner.extract_keywords(cleaned_text)
        }
        
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
                'education_entries': len(extracted_data['education']),
                'experience_entries': len(extracted_data['experience']),
                'contact_info': extracted_data['contact']
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
        cleaned_text = cleaner.full_preprocessing(raw_text)
        
        # Extract sections
        extractor = SectionExtractor()
        sections = extractor.extract_sections(raw_text)
        
        # Extract structured data
        extracted_data = {
            'required_skills': extractor.extract_skills(raw_text),
            'keywords': cleaner.extract_keywords(cleaned_text)
        }
        
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