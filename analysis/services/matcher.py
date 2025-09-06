from typing import Dict, Any, List
import re


def calculate_compatibility(resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula a compatibilidade entre currículo e vaga
    """
    job_text = job_data.get('description', '').lower() + ' ' + job_data.get('title', '').lower()
    resume_text = resume_data.get('raw_text', '').lower()
    
    # Extrai habilidades da vaga
    job_skills = extract_skills_from_text(job_text)
    
    # Habilidades do currículo
    resume_skills = resume_data.get('skills', [])
    
    # Calcula match de habilidades
    skills_match = calculate_skills_match(resume_skills, job_skills)
    
    # Calcula outros fatores
    keyword_match = calculate_keyword_match(resume_text, job_text)
    experience_match = calculate_experience_match(resume_data, job_text)
    
    # Score geral (ponderado)
    overall_score = (
        skills_match['score'] * 0.4 +
        keyword_match * 0.3 +
        experience_match * 0.3
    )
    
    return {
        'overall_score': round(overall_score, 2),
        'skills_match': skills_match,
        'keyword_match': round(keyword_match, 2),
        'experience_match': round(experience_match, 2),
        'missing_skills': skills_match['missing'],
        'matching_skills': skills_match['matching'],
        'job_skills': job_skills
    }


def extract_skills_from_text(text: str) -> List[str]:
    """Extrai habilidades de um texto"""
    common_skills = [
        'python', 'java', 'javascript', 'typescript', 'html', 'css', 'react',
        'angular', 'vue', 'node.js', 'django', 'flask', 'fastapi', 'sql',
        'nosql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'gcp',
        'docker', 'kubernetes', 'git', 'jenkins', 'linux', 'agile', 'scrum',
        'rest', 'graphql', 'microservices', 'ci/cd', 'terraform', 'ansible'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in common_skills:
        if skill in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicates


def calculate_skills_match(resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
    """Calcula o match de habilidades"""
    if not job_skills:
        return {'score': 0.0, 'matching': [], 'missing': []}
    
    matching_skills = [skill for skill in job_skills if skill in resume_skills]
    missing_skills = [skill for skill in job_skills if skill not in resume_skills]
    
    score = len(matching_skills) / len(job_skills) if job_skills else 0.0
    
    return {
        'score': round(score, 2),
        'matching': matching_skills,
        'missing': missing_skills
    }


def calculate_keyword_match(resume_text: str, job_text: str) -> float:
    """Calcula o match de keywords importantes"""
    # Extrai palavras importantes da vaga (excluindo stopwords)
    words = re.findall(r'[a-z]{4,}', job_text)
    word_freq = {}
    
    for word in words:
        if word not in ['para', 'com', 'como', 'sobre', 'sobre', 'para', 'sobre']:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Pega as 20 palavras mais frequentes
    important_words = sorted(word_freq, key=word_freq.get, reverse=True)[:20]
    
    if not important_words:
        return 0.0
    
    # Calcula quantas estão no currículo
    matches = sum(1 for word in important_words if word in resume_text)
    
    return matches / len(important_words)


def calculate_experience_match(resume_data: Dict[str, Any], job_text: str) -> float:
    """Calcula o match de experiência"""
    # Verifica termos de senioridade na vaga
    seniority_terms = {
        'junior': 1,
        'pleno': 2,
        'senior': 3,
        'sênior': 3,
        'especialista': 4,
        'lead': 4,
        'manager': 5
    }
    
    job_seniority = 0
    for term, level in seniority_terms.items():
        if term in job_text:
            job_seniority = max(job_seniority, level)
    
    # Simula senioridade baseada na experiência (simplificado)
    resume_experience = len(resume_data.get('experience', []))
    resume_seniority = min(5, resume_experience)  # Máximo 5
    
    if job_seniority == 0:
        return 0.7  # Se não especificado, assume match médio
    
    # Calcula match de senioridade
    seniority_diff = abs(resume_seniority - job_seniority)
    if seniority_diff == 0:
        return 1.0
    elif seniority_diff == 1:
        return 0.7
    elif seniority_diff == 2:
        return 0.4
    else:
        return 0.1
