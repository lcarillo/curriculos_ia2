import PyPDF2
import docx
import json
import re
from typing import Dict, Any


def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Extrai informações de um currículo (PDF ou DOCX)
    """
    file_ext = file_path.lower().split('.')[-1]
    
    if file_ext == 'pdf':
        return parse_pdf(file_path)
    elif file_ext in ['doc', 'docx']:
        return parse_docx(file_path)
    else:
        raise ValueError(f"Formato de arquivo não suportado: {file_ext}")


def parse_pdf(file_path: str) -> Dict[str, Any]:
    """
    Extrai texto de um PDF e parseia informações do currículo
    """
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    
    return extract_info_from_text(text)


def parse_docx(file_path: str) -> Dict[str, Any]:
    """
    Extrai texto de um DOCX e parseia informações do currículo
    """
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    return extract_info_from_text(text)


def extract_info_from_text(text: str) -> Dict[str, Any]:
    """
    Extrai informações estruturadas do texto do currículo
    """
    # Esta é uma implementação básica - em produção, usaríamos ML/NLP
    lines = text.split('\n')
    
    info = {
        'name': extract_name(lines),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'education': extract_education(lines),
        'experience': extract_experience(lines),
        'skills': extract_skills(text),
        'languages': extract_languages(text),
        'raw_text': text
    }
    
    return info


def extract_name(lines):
    """Tenta extrair o nome do currículo (primeira linha não vazia)"""
    for line in lines:
        line = line.strip()
        if line and not line.startswith(('http', 'www', '@')):
            # Verifica se parece um nome (não apenas uma palavra, não apenas números)
            if len(line.split()) >= 2 and not any(char.isdigit() for char in line):
                return line
    return "Nome não identificado"


def extract_email(text):
    """Extrai email do texto"""
    email_pattern = '\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else "Email não identificado"


def extract_phone(text):
    """Extrai telefone do texto"""
    phone_pattern = r'(\+55\s?)?(\(?\d{2}\)?[\s-]?)(\d{4,5}[\s-]?\d{4})'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else "Telefone não identificado"


def extract_education(lines):
    """Extrai informações de educação (simplificado)"""
    education = []
    edu_keywords = ['graduação', 'bacharel', 'mestrado', 'doutorado', 'curso', 'faculdade', 'universidade']
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in edu_keywords):
            # Pega as próximas linhas como contexto
            context = line
            for j in range(1, 4):
                if i + j < len(lines):
                    context += " " + lines[i + j]
            education.append(context.strip())
    
    return education[:3]  # Retorna no máximo 3 entradas


def extract_experience(lines):
    """Extrai informações de experiência (simplificado)"""
    experience = []
    exp_keywords = ['experiência', 'profissional', 'empresa', 'trabalho', 'cargo']
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in exp_keywords):
            # Pega as próximas linhas como contexto
            context = line
            for j in range(1, 6):
                if i + j < len(lines):
                    context += " " + lines[i + j]
            experience.append(context.strip())
    
    return experience[:5]  # Retorna no máximo 5 entradas


def extract_skills(text):
    """Extrai habilidades do texto"""
    skills = []
    common_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'react', 'angular', 'vue',
        'node.js', 'django', 'flask', 'sql', 'nosql', 'mongodb', 'postgresql',
        'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'agile', 'scrum'
    ]
    
    text_lower = text.lower()
    for skill in common_skills:
        if skill in text_lower:
            skills.append(skill)
    
    return skills[:10]  # Retorna no máximo 10 habilidades


def extract_languages(text):
    """Extrai idiomas do texto"""
    languages = []
    lang_keywords = ['português', 'inglês', 'espanhol', 'francês', 'alemão', 'italiano']
    
    text_lower = text.lower()
    for lang in lang_keywords:
        if lang in text_lower:
            languages.append(lang)
    
    return languages
