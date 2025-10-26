# parser/utils/section_extractor.py

import re
from collections import Counter

class SectionExtractor:
    """Extract structured sections from resume text"""
    
    def __init__(self):
        # Define section headers
        self.section_patterns = {
            'education': [
                r'education', r'academic', r'qualification', r'degree', 
                r'university', r'college', r'school'
            ],
            'experience': [
                r'experience', r'employment', r'work history', r'professional experience',
                r'work experience', r'career', r'work\s+experience'
            ],
            'skills': [
                r'skills', r'technical skills', r'competencies', r'expertise',
                r'proficiencies', r'technologies', r'technical\s+skills'
            ],
            'projects': [
                r'projects', r'personal projects', r'academic projects'
            ],
            'certifications': [
                r'certification', r'certificate', r'license', r'accreditation'
            ],
            'summary': [
                r'summary', r'objective', r'profile', r'about me', r'introduction'
            ]
        }
        
        # Comprehensive technical skills database
        self.skill_keywords = {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c', 'c++', 'c#', 'go', 'rust',
            'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl',
            
            # Web Frameworks & Libraries
            'django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'vue.js',
            'node.js', 'nodejs', 'express', 'spring', 'spring boot', 'asp.net',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra',
            'elasticsearch', 'dynamodb', 'oracle', 'sqlite', 'mariadb',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
            'jenkins', 'terraform', 'ansible', 'ci/cd', 'github actions',
            
            # Data Science & ML
            'machine learning', 'deep learning', 'nlp', 'ai', 'artificial intelligence',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'matplotlib', 'seaborn', 'opencv', 'mlops',
            
            # Big Data
            'spark', 'hadoop', 'kafka', 'airflow', 'databricks', 'snowflake',
            'etl', 'data pipeline', 'azure data factory', 'synapse',
            
            # Tools & Others
            'git', 'github', 'gitlab', 'jira', 'confluence', 'postman',
            'vscode', 'linux', 'unix', 'bash', 'powershell',
            'rest api', 'graphql', 'microservices', 'agile', 'scrum',
            
            # Web Technologies
            'html', 'css', 'sass', 'bootstrap', 'tailwind', 'webpack',
            'jquery', 'ajax', 'json', 'xml', 'yaml',
            
            # Testing
            'pytest', 'junit', 'selenium', 'jest', 'mocha', 'unittest',
            
            # Other
            'tableau', 'power bi', 'excel', 'dvc', 'langchain', 'langgraph'
        }
    
    def extract_sections(self, text):
        """
        Extract sections from resume text with better boundary detection
        
        :param text: Raw resume text
        :return: Dictionary with section names as keys
        """
        sections = {}
        lines = text.split('\n')
        
        current_section = 'other'
        current_content = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Check if line is a section header (usually short and matches pattern)
            is_header = False
            if len(line_stripped) < 50:  # Headers are typically short
                for section_name, patterns in self.section_patterns.items():
                    for pattern in patterns:
                        if re.search(r'^' + pattern + r'$', line_lower) or \
                           re.search(r'^' + pattern + r'\s*$', line_lower) or \
                           re.search(r'^' + pattern + r':?\s*$', line_lower):
                            # Save previous section
                            if current_content:
                                if current_section not in sections:
                                    sections[current_section] = []
                                sections[current_section].append('\n'.join(current_content))
                            
                            # Start new section
                            current_section = section_name
                            current_content = []
                            is_header = True
                            break
                    if is_header:
                        break
            
            # Add line to current section if it's not a header
            if not is_header:
                current_content.append(line_stripped)
        
        # Add last section
        if current_content:
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].append('\n'.join(current_content))
        
        # Combine multiple occurrences of same section
        for key in sections:
            sections[key] = '\n\n'.join(sections[key])
        
        return sections
    
    def extract_skills(self, text, sections=None):
        """
        Extract skills with improved cleaning and context awareness
        
        :param text: Resume text
        :param sections: Pre-extracted sections (optional)
        :return: List of unique, cleaned skills
        """
        skills = set()
        
        # If sections provided, focus on skills section first
        search_text = text
        if sections and 'skills' in sections:
            search_text = sections['skills']
        
        # Normalize text for matching
        text_lower = search_text.lower()
        
        # Remove excessive whitespace
        text_lower = re.sub(r'\s+', ' ', text_lower)
        
        # Extract skills using keyword matching
        for skill in self.skill_keywords:
            # Use word boundary for exact matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                # Capitalize properly
                if skill in ['sql', 'html', 'css', 'xml', 'json', 'yaml', 'aws', 'gcp', 'nlp', 'ai', 'etl', 'ci/cd', 'rest api']:
                    skills.add(skill.upper())
                elif '.' in skill:  # node.js, vue.js
                    skills.add(skill)
                else:
                    skills.add(skill.title())
        
        # Also check full text for additional patterns
        if sections:
            full_text = text.lower()
            full_text = re.sub(r'\s+', ' ', full_text)
            
            for skill in self.skill_keywords:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, full_text) and skill not in [s.lower() for s in skills]:
                    if skill in ['sql', 'html', 'css', 'xml', 'json', 'yaml', 'aws', 'gcp', 'nlp', 'ai', 'etl', 'ci/cd']:
                        skills.add(skill.upper())
                    elif '.' in skill:
                        skills.add(skill)
                    else:
                        skills.add(skill.title())
        
        return sorted(list(skills))
    
    def extract_education(self, text, sections=None):
        """
        Extract education information with better grouping
        
        :param text: Resume text
        :param sections: Pre-extracted sections (optional)
        :return: List of education entries (grouped by institution)
        """
        education = []
        
        # Use education section if available
        search_text = text
        if sections and 'education' in sections:
            search_text = sections['education']
        
        # Split by double newlines or obvious institution markers
        lines = search_text.split('\n')
        current_education = []
        found_institution = False
        
        # Patterns for institutions
        institution_patterns = [
            r'university', r'college', r'institute', r'school', r'academy'
        ]
        
        # Degree patterns
        degree_patterns = [
            r"(?:bachelor|master|phd|doctorate|associate)(?:'?s)?",
            r"b\.?\s*s\.?", r"m\.?\s*s\.?", r"b\.?\s*a\.?", r"m\.?\s*a\.?",
            r"b\.?\s*tech", r"m\.?\s*tech", r"b\.?\s*e\.?", r"m\.?\s*e\.?"
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                # Empty line might indicate end of education entry
                if current_education and found_institution:
                    education.append('\n'.join(current_education))
                    current_education = []
                    found_institution = False
                continue
            
            line_lower = line.lower()
            
            # Check if line contains institution name
            has_institution = any(re.search(pattern, line_lower) for pattern in institution_patterns)
            
            # Check if line contains degree
            has_degree = any(re.search(pattern, line_lower) for pattern in degree_patterns)
            
            # If we find an institution, start a new education block
            if has_institution:
                if current_education and found_institution:
                    # Save previous education
                    education.append('\n'.join(current_education))
                # Start new education block
                current_education = [line]
                found_institution = True
            elif has_degree and not found_institution:
                # Degree line without institution yet - start new block
                if current_education:
                    education.append('\n'.join(current_education))
                current_education = [line]
                found_institution = True
            elif current_education:
                # Add to current education entry
                # But don't add if it looks like start of another section
                if not re.search(r'^(experience|skills|projects|certifications):', line_lower):
                    current_education.append(line)
        
        # Add last entry
        if current_education and found_institution:
            education.append('\n'.join(current_education))
        
        return education
    
    def extract_experience(self, text, sections=None):
        """
        Extract work experience with improved date matching and job title detection
        
        :param text: Resume text
        :param sections: Pre-extracted sections (optional)
        :return: List of experience entries
        """
        experiences = []
        
        # Use experience section if available
        search_text = text
        if sections and 'experience' in sections:
            search_text = sections['experience']
        
        # Improved date patterns to match various formats
        date_patterns = [
            r'\d{4}\s*[-–—]\s*(?:\d{4}|present|current)',  # 2023 - 2024
            r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{4}\s*[-–—]\s*(?:(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{4}|present|current)',  # March 2023 - Aug 2024
            r'\d{1,2}/\d{4}\s*[-–—]\s*(?:\d{1,2}/\d{4}|present|current)',  # 03/2023 - 08/2024
        ]
        
        # Job title indicators (often appears with | separator)
        job_title_pattern = r'\b(?:developer|engineer|analyst|manager|lead|senior|junior|intern|internship|consultant|architect|designer|specialist)\b'
        
        lines = search_text.split('\n')
        current_exp = []
        found_date_or_title = False
        
        for line in lines:
            line = line.strip()
            if not line:
                # Empty line - end of experience entry
                if current_exp and found_date_or_title:
                    experiences.append('\n'.join(current_exp))
                    current_exp = []
                    found_date_or_title = False
                continue
            
            line_lower = line.lower()
            
            # Check if line contains a date range
            has_date = any(re.search(pattern, line_lower) for pattern in date_patterns)
            
            # Check if line looks like job title (contains job keywords and possibly |)
            has_job_title = re.search(job_title_pattern, line_lower) and ('|' in line or len(line) < 80)
            
            if has_date or (has_job_title and not current_exp):
                # Start new experience entry
                if current_exp and found_date_or_title:
                    experiences.append('\n'.join(current_exp))
                current_exp = [line]
                found_date_or_title = True
            elif current_exp:
                # Add to current experience
                # Don't add if it looks like start of another section
                if not re.search(r'^(education|skills|projects|certifications):', line_lower):
                    current_exp.append(line)
        
        # Add last experience
        if current_exp and found_date_or_title:
            experiences.append('\n'.join(current_exp))
        
        return experiences
    
    def extract_contact_info(self, text):
        """
        Extract contact information with improved regex
        
        :param text: Resume text
        :return: Dictionary with contact details
        """
        contact = {
            'email': None,
            'phone': None,
            'linkedin': None
        }
        
        # Improved email pattern - must start with alphanumeric, not just digit
        email_pattern = r'\b[A-Za-z][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group()
        
        # If no email found with strict pattern, try more permissive (allows starting with digit)
        if not contact['email']:
            email_pattern_permissive = r'\b[A-Za-z0-9][A-Za-z0-9._%+-]{2,}@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern_permissive, text)
            if email_match:
                contact['email'] = email_match.group()
        
        # Improved phone pattern
        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group()
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9_-]+'
        linkedin_match = re.search(linkedin_pattern, text.lower())
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group()
        
        return contact