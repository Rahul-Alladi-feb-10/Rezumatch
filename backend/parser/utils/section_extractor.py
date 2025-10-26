# parser/utils/section_extractor.py

import re
import spacy

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


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
                r'work experience', r'career'
            ],
            'skills': [
                r'skills', r'technical skills', r'competencies', r'expertise',
                r'proficiencies', r'technologies'
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
    
    def extract_sections(self, text):
        """
        Extract sections from resume text
        
        :param text: Raw resume text
        :return: Dictionary with section names as keys
        """
        sections = {}
        lines = text.split('\n')
        
        current_section = 'other'
        current_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if line is a section header
            section_found = False
            for section_name, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.search(r'\b' + pattern + r'\b', line_lower):
                        # Save previous section
                        if current_content:
                            if current_section not in sections:
                                sections[current_section] = []
                            sections[current_section].append('\n'.join(current_content))
                        
                        # Start new section
                        current_section = section_name
                        current_content = []
                        section_found = True
                        break
                if section_found:
                    break
            
            # Add line to current section if it's not a header
            if not section_found and line.strip():
                current_content.append(line)
        
        # Add last section
        if current_content:
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].append('\n'.join(current_content))
        
        # Combine multiple occurrences of same section
        for key in sections:
            sections[key] = '\n\n'.join(sections[key])
        
        return sections
    
    def extract_skills(self, text):
        """
        Extract skills using NER and pattern matching
        
        :param text: Resume text
        :return: List of extracted skills
        """
        doc = nlp(text)
        skills = set()
        
        # Common technical skills (you can expand this list)
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'node.js', 
            'django', 'flask', 'sql', 'mongodb', 'postgresql', 'aws', 'azure',
            'docker', 'kubernetes', 'git', 'machine learning', 'deep learning',
            'nlp', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'
        ]
        
        # Extract from text
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                skills.add(skill.title())
        
        # Extract organizations and products (often skills/technologies)
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT'] and len(ent.text) > 2:
                skills.add(ent.text)
        
        return list(skills)
    
    def extract_education(self, text):
        """
        Extract education information
        
        :param text: Resume text
        :return: List of education entries
        """
        doc = nlp(text)
        education = []
        
        # Look for degree patterns
        degree_patterns = [
            r'(bachelor|master|phd|doctorate|associate|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?)',
            r'(b\.?tech|m\.?tech|b\.?e\.?|m\.?e\.?)'
        ]
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            for pattern in degree_patterns:
                if re.search(pattern, line_lower):
                    education.append(line.strip())
                    break
        
        return education
    
    def extract_experience(self, text):
        """
        Extract work experience
        
        :param text: Resume text
        :return: List of experience entries
        """
        doc = nlp(text)
        experiences = []
        
        # Look for job title patterns and date ranges
        date_pattern = r'\d{4}\s*[-–]\s*(\d{4}|present|current)'
        
        lines = text.split('\n')
        current_exp = []
        
        for i, line in enumerate(lines):
            # Check if line contains a date range
            if re.search(date_pattern, line.lower()):
                if current_exp:
                    experiences.append('\n'.join(current_exp))
                current_exp = [line]
            elif current_exp and line.strip():
                current_exp.append(line)
            elif not line.strip() and current_exp:
                experiences.append('\n'.join(current_exp))
                current_exp = []
        
        # Add last experience
        if current_exp:
            experiences.append('\n'.join(current_exp))
        
        return experiences
    
    def extract_contact_info(self, text):
        """
        Extract contact information
        
        :param text: Resume text
        :return: Dictionary with contact details
        """
        contact = {
            'email': None,
            'phone': None,
            'linkedin': None
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group()
        
        # Extract phone
        phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group()
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text.lower())
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group()
        
        return contact