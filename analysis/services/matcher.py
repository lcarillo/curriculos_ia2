# ===== Arquivo: C:\Users\lcarillo\Desktop\curriculos_ia1\analysis\services\matcher.py =====

from typing import Dict, Any, List, Tuple
import re
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


def calculate_compatibility(resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula a compatibilidade entre currículo e vaga de forma mais robusta
    """
    try:
        # Garantir que os dados são dicionários
        if not isinstance(resume_data, dict):
            logger.warning(f"resume_data não é dicionário: {type(resume_data)}")
            resume_data = {}

        if not isinstance(job_data, dict):
            logger.warning(f"job_data não é dicionário: {type(job_data)}")
            job_data = {}

        # Preparar textos para análise com valores padrão
        job_text = prepare_job_text(job_data)
        resume_text = prepare_resume_text(resume_data)

        # Análises detalhadas com tratamento de erro
        skills_analysis = analyze_skills_match(resume_data, job_data, job_text)
        keyword_analysis = analyze_keywords_match(resume_text, job_text)
        experience_analysis = analyze_experience_match(resume_data, job_data)
        education_analysis = analyze_education_match(resume_data, job_data)

        # Score geral ponderado
        overall_score = calculate_overall_score(
            skills_analysis,
            keyword_analysis,
            experience_analysis,
            education_analysis
        )

        return {
            'overall_score': min(round(overall_score, 2), 100.0),
            'skills_analysis': skills_analysis,
            'keyword_analysis': keyword_analysis,
            'experience_analysis': experience_analysis,
            'education_analysis': education_analysis,
            'detailed_breakdown': generate_detailed_breakdown(
                skills_analysis, keyword_analysis, experience_analysis, education_analysis
            )
        }
    except Exception as e:
        logger.error(f"Erro no cálculo de compatibilidade: {str(e)}")
        # Retornar resultado fallback
        return get_fallback_analysis_result()


def prepare_job_text(job_data: Dict[str, Any]) -> str:
    """Prepara texto da vaga para análise com valores padrão"""
    if not job_data:
        return ""

    text_parts = [
        job_data.get('title', ''),
        job_data.get('description', ''),
        job_data.get('requirements', ''),
        job_data.get('responsibilities', ''),
        job_data.get('qualifications', ''),
        ' '.join(job_data.get('skills', [])),
        job_data.get('company', '')
    ]
    return ' '.join(str(part) for part in text_parts if part).lower()


def prepare_resume_text(resume_data: Dict[str, Any]) -> str:
    """Prepara texto do currículo para análise com valores padrão"""
    if not resume_data:
        return ""

    text_parts = [
        resume_data.get('raw_text', ''),
        ' '.join(resume_data.get('skills', [])),
    ]

    # Experiência profissional
    experience = resume_data.get('experience', [])
    if isinstance(experience, list):
        exp_descriptions = []
        for exp in experience:
            if isinstance(exp, dict):
                exp_descriptions.append(exp.get('description', ''))
            else:
                exp_descriptions.append(str(exp))
        text_parts.append(' '.join(exp_descriptions))

    # Educação
    education = resume_data.get('education', [])
    if isinstance(education, list):
        edu_descriptions = []
        for edu in education:
            if isinstance(edu, dict):
                edu_descriptions.append(edu.get('degree', '') + ' ' + edu.get('field', ''))
            else:
                edu_descriptions.append(str(edu))
        text_parts.append(' '.join(edu_descriptions))

    text_parts.append(resume_data.get('summary', ''))

    return ' '.join(str(part) for part in text_parts if part).lower()


def analyze_skills_match(resume_data: Dict[str, Any], job_data: Dict[str, Any], job_text: str) -> Dict[str, Any]:
    """Análise detalhada de compatibilidade de habilidades com tratamento robusto"""
    try:
        job_skills = extract_skills_with_importance(job_text)
        resume_skills = extract_resume_skills(resume_data)

        exact_matches = []
        similar_matches = []
        missing_skills = []

        for job_skill in job_skills:
            found = False
            for resume_skill in resume_skills:
                similarity = calculate_skill_similarity(job_skill['name'], resume_skill['name'])

                if similarity >= 0.9:
                    exact_matches.append({
                        'job_skill': job_skill,
                        'resume_skill': resume_skill,
                        'similarity': similarity
                    })
                    found = True
                    break
                elif similarity >= 0.7:
                    similar_matches.append({
                        'job_skill': job_skill,
                        'resume_skill': resume_skill,
                        'similarity': similarity
                    })
                    found = True
                    break

            if not found:
                missing_skills.append(job_skill)

        total_skills = len(job_skills)
        if total_skills == 0:
            score = 0.0
        else:
            exact_weight = len(exact_matches) * 1.0
            similar_weight = len(similar_matches) * 0.7
            score = min((exact_weight + similar_weight) / total_skills, 1.0)

        return {
            'score': round(score * 100, 2),
            'exact_matches': exact_matches,
            'similar_matches': similar_matches,
            'missing_skills': missing_skills,
            'job_skills_count': total_skills,
            'resume_skills_count': len(resume_skills)
        }
    except Exception as e:
        logger.error(f"Erro na análise de habilidades: {str(e)}")
        return {
            'score': 0,
            'exact_matches': [],
            'similar_matches': [],
            'missing_skills': [],
            'job_skills_count': 0,
            'resume_skills_count': 0
        }


def extract_skills_with_importance(text: str) -> List[Dict[str, Any]]:
    """Extrai habilidades do texto com nível de importância"""
    skills_db = {
        'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin'],
        'web': ['html', 'css', 'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js', 'express'],
        'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server'],
        'cloud': ['aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'terraform'],
        'data_science': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'machine learning', 'deep learning'],
        'tools': ['git', 'jenkins', 'jira', 'confluence', 'slack', 'docker', 'kubernetes'],
        'methodologies': ['agile', 'scrum', 'kanban', 'devops', 'ci/cd']
    }

    found_skills = []
    if not text:
        return found_skills

    text_lower = text.lower()

    for category, skills in skills_db.items():
        for skill in skills:
            if skill in text_lower:
                importance = 1.0
                context_indicators = [
                    f"experiência em {skill}", f"conhecimento em {skill}", f"domínio de {skill}",
                    f"forte conhecimento em {skill}", f"expertise em {skill}", f"proficiente em {skill}"
                ]

                for indicator in context_indicators:
                    if indicator in text_lower:
                        importance += 0.5

                # Verificar se é um requisito obrigatório
                if f"requisito: {skill}" in text_lower or f"obrigatório: {skill}" in text_lower:
                    importance += 1.0

                found_skills.append({
                    'name': skill,
                    'category': category,
                    'importance': min(importance, 3.0),
                    'found_in_context': extract_skill_context(text_lower, skill)
                })

    return found_skills


def extract_resume_skills(resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extrai habilidades do currículo com tratamento robusto"""
    skills = []

    if not resume_data:
        return skills

    # Skills explícitos
    resume_skills = resume_data.get('skills', [])
    if not isinstance(resume_skills, list):
        resume_skills = [resume_skills] if resume_skills else []

    for skill in resume_skills:
        if isinstance(skill, dict):
            skills.append({
                'name': skill.get('name', '').lower(),
                'category': skill.get('category', 'other'),
                'proficiency': skill.get('proficiency', 'intermediate'),
                'years': skill.get('years', 0)
            })
        else:
            skills.append({
                'name': str(skill).lower(),
                'category': 'other',
                'proficiency': 'intermediate',
                'years': 0
            })

    # Extrair skills da experiência
    experience = resume_data.get('experience', [])
    if isinstance(experience, list):
        for exp in experience:
            if isinstance(exp, dict):
                description = exp.get('description', '').lower()
                for skill in extract_skills_from_text(description):
                    skills.append({
                        'name': skill,
                        'category': 'experienced',
                        'proficiency': 'advanced',
                        'years': calculate_years_from_experience(exp)
                    })

    return skills


def analyze_keywords_match(resume_text: str, job_text: str) -> Dict[str, Any]:
    """Análise de palavras-chave com tratamento robusto"""
    try:
        job_keywords = extract_important_keywords(job_text)

        matches = []
        missing = []

        for keyword, weight in job_keywords:
            if keyword in resume_text:
                frequency = resume_text.count(keyword)
                context_score = calculate_context_relevance(resume_text, keyword)
                match_score = min((frequency * 0.3) + (context_score * 0.7), 1.0) * weight

                matches.append({
                    'keyword': keyword,
                    'weight': weight,
                    'frequency': frequency,
                    'context_score': context_score,
                    'match_score': match_score
                })
            else:
                missing.append({
                    'keyword': keyword,
                    'weight': weight,
                    'reason': 'not_found'
                })

        total_weight = sum(weight for keyword, weight in job_keywords)
        matched_weight = sum(match['match_score'] for match in matches)

        score = (matched_weight / total_weight * 100) if total_weight > 0 else 0

        return {
            'score': round(score, 2),
            'matches': matches,
            'missing_keywords': missing,
            'total_keywords': len(job_keywords)
        }
    except Exception as e:
        logger.error(f"Erro na análise de keywords: {str(e)}")
        return {
            'score': 0,
            'matches': [],
            'missing_keywords': [],
            'total_keywords': 0
        }


def extract_important_keywords(text: str) -> List[Tuple[str, float]]:
    """Extrai palavras-chave importantes do texto com pesos"""
    if not text:
        return []

    words = re.findall(r'\b[a-z]{4,15}\b', text.lower())

    # Remover stopwords
    stopwords = {'para', 'com', 'como', 'sobre', 'para', 'sobre', 'mais', 'muito', 'seu', 'sua'}
    filtered_words = [word for word in words if word not in stopwords]

    # Calcular frequência e importância
    word_freq = {}
    for word in filtered_words:
        word_freq[word] = word_freq.get(word, 0) + 1

    # Ordenar por frequência e atribuir pesos
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:30]

    # Atribuir pesos baseados na posição (mais frequente = maior peso)
    keywords_with_weight = []
    max_freq = sorted_words[0][1] if sorted_words else 1

    for i, (word, freq) in enumerate(sorted_words):
        weight = 0.3 + (0.7 * (freq / max_freq))  # Peso entre 0.3 e 1.0
        keywords_with_weight.append((word, weight))

    return keywords_with_weight


def analyze_experience_match(resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Análise de compatibilidade de experiência com tratamento robusto"""
    try:
        resume_experience = resume_data.get('experience', []) if resume_data else []
        job_requirements = job_data.get('requirements', '') if job_data else ''

        seniority_match = analyze_seniority_match(resume_experience, job_requirements)
        relevance_match = analyze_experience_relevance(resume_experience, job_data)
        duration_match = analyze_experience_duration(resume_experience, job_requirements)

        total_score = (
                seniority_match.get('score', 0) * 0.4 +
                relevance_match.get('score', 0) * 0.4 +
                duration_match.get('score', 0) * 0.2
        )

        return {
            'score': round(total_score, 2),
            'seniority_analysis': seniority_match,
            'relevance_analysis': relevance_match,
            'duration_analysis': duration_match,
            'total_experience_years': calculate_total_experience_years(resume_experience)
        }
    except Exception as e:
        logger.error(f"Erro na análise de experiência: {str(e)}")
        return {
            'score': 0,
            'seniority_analysis': {'score': 0},
            'relevance_analysis': {'score': 0},
            'duration_analysis': {'score': 0},
            'total_experience_years': 0
        }


def analyze_education_match(resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Análise de compatibilidade educacional com tratamento robusto"""
    try:
        resume_education = resume_data.get('education', []) if resume_data else []
        job_requirements = (
                    job_data.get('requirements', '') + ' ' + job_data.get('description', '')) if job_data else ''

        education_requirements = extract_education_requirements(job_requirements)
        matches = []
        missing = []

        for requirement in education_requirements:
            found = False
            for education in resume_education:
                if isinstance(education, dict) and requirement['level'] in education.get('degree', '').lower():
                    matches.append({
                        'requirement': requirement,
                        'education': education,
                        'match_type': 'exact'
                    })
                    found = True
                    break

            if not found:
                missing.append(requirement)

        total_requirements = len(education_requirements)
        score = (len(matches) / total_requirements * 100) if total_requirements > 0 else 100

        return {
            'score': round(score, 2),
            'matches': matches,
            'missing_requirements': missing,
            'resume_education': resume_education
        }
    except Exception as e:
        logger.error(f"Erro na análise de educação: {str(e)}")
        return {
            'score': 0,
            'matches': [],
            'missing_requirements': [],
            'resume_education': []
        }


def get_fallback_analysis_result() -> Dict[str, Any]:
    """Retorna resultado fallback para análise com erro"""
    return {
        'overall_score': 0,
        'skills_analysis': {
            'score': 0,
            'exact_matches': [],
            'similar_matches': [],
            'missing_skills': [],
            'job_skills_count': 0,
            'resume_skills_count': 0
        },
        'keyword_analysis': {
            'score': 0,
            'matches': [],
            'missing_keywords': [],
            'total_keywords': 0
        },
        'experience_analysis': {
            'score': 0,
            'seniority_analysis': {'score': 0, 'level': 'unknown', 'years': 0},
            'relevance_analysis': {'score': 0},
            'duration_analysis': {'score': 0},
            'total_experience_years': 0
        },
        'education_analysis': {
            'score': 0,
            'matches': [],
            'missing_requirements': [],
            'resume_education': []
        },
        'detailed_breakdown': {
            'strengths': ['Análise básica concluída'],
            'weaknesses': ['Erro durante o processamento detalhado'],
            'recommendations': ['Tente novamente ou verifique os dados de entrada']
        }
    }


def calculate_overall_score(skills_analysis: Dict, keyword_analysis: Dict,
                            experience_analysis: Dict, education_analysis: Dict) -> float:
    """Calcula score geral ponderado"""
    return (
            skills_analysis.get('score', 0) * 0.35 +
            keyword_analysis.get('score', 0) * 0.30 +
            experience_analysis.get('score', 0) * 0.25 +
            education_analysis.get('score', 0) * 0.10
    )


def generate_detailed_breakdown(skills_analysis, keyword_analysis, experience_analysis, education_analysis):
    """Gera breakdown detalhado da análise"""
    return {
        'strengths': identify_strengths(skills_analysis, keyword_analysis, experience_analysis, education_analysis),
        'weaknesses': identify_weaknesses(skills_analysis, keyword_analysis, experience_analysis, education_analysis),
        'recommendations': generate_recommendations(skills_analysis, keyword_analysis, experience_analysis,
                                                    education_analysis)
    }


def identify_strengths(skills_analysis, keyword_analysis, experience_analysis, education_analysis):
    """Identifica pontos fortes"""
    strengths = []

    if skills_analysis.get('score', 0) >= 80:
        strengths.append("Excelente compatibilidade de habilidades técnicas")
    elif skills_analysis.get('score', 0) >= 60:
        strengths.append("Boa base de habilidades técnicas")

    if keyword_analysis.get('score', 0) >= 80:
        strengths.append("Currículo bem alinhado com as palavras-chave da vaga")

    if experience_analysis.get('score', 0) >= 70:
        strengths.append("Experiência relevante para a posição")

    return strengths


def identify_weaknesses(skills_analysis, keyword_analysis, experience_analysis, education_analysis):
    """Identifica pontos fracos"""
    weaknesses = []

    if skills_analysis.get('score', 0) < 50:
        weaknesses.append(f"Faltam {len(skills_analysis.get('missing_skills', []))} habilidades importantes")

    if keyword_analysis.get('score', 0) < 60:
        weaknesses.append("Baixa densidade de palavras-chave relevantes")

    if experience_analysis.get('score', 0) < 50:
        weaknesses.append("Experiência abaixo do necessário para a posição")

    return weaknesses


def generate_recommendations(skills_analysis, keyword_analysis, experience_analysis, education_analysis):
    """Gera recomendações específicas"""
    recommendations = []

    # Recomendações baseadas em habilidades faltantes
    for skill in skills_analysis.get('missing_skills', [])[:5]:
        recommendations.append(f"Adicionar habilidade: {skill.get('name', '')}")

    # Recomendações de keywords
    if keyword_analysis.get('score', 0) < 70:
        missing_keywords = [kw.get('keyword', '') for kw in keyword_analysis.get('missing_keywords', [])[:5]]
        recommendations.append(f"Incluir palavras-chave: {', '.join(missing_keywords)}")

    return recommendations


# Funções auxiliares
def calculate_skill_similarity(skill1: str, skill2: str) -> float:
    try:
        return SequenceMatcher(None, skill1.lower(), skill2.lower()).ratio()
    except:
        return 0.0


def extract_skill_context(text: str, skill: str) -> str:
    """Extrai contexto onde a skill é mencionada"""
    try:
        words = text.split()
        index = words.index(skill)
        start = max(0, index - 5)
        end = min(len(words), index + 6)
        return ' '.join(words[start:end])
    except:
        return skill


def extract_skills_from_text(text: str) -> List[str]:
    try:
        common_skills = ['python', 'java', 'javascript', 'html', 'css', 'react', 'angular', 'vue',
                         'node.js', 'django', 'flask', 'sql', 'nosql', 'mongodb', 'postgresql',
                         'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'agile', 'scrum']

        found_skills = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill)

        return found_skills
    except:
        return []


def calculate_context_relevance(text: str, keyword: str) -> float:
    """Calcula relevância baseada no contexto (implementação simplificada)"""
    try:
        # Verificar se a keyword está em contexto importante
        important_indicators = [
            'experiência', 'conhecimento', 'domínio', 'habilidade', 'competência',
            'responsabilidade', 'atividade', 'projeto'
        ]

        words = text.split()
        if keyword in words:
            index = words.index(keyword)
            # Verificar palavras próximas
            start = max(0, index - 3)
            end = min(len(words), index + 4)
            context = ' '.join(words[start:end])

            # Se estiver perto de palavras importantes, aumenta a relevância
            for indicator in important_indicators:
                if indicator in context:
                    return 0.9

        return 0.5
    except:
        return 0.3


def calculate_years_from_experience(experience: Dict) -> int:
    try:
        return experience.get('years', 1)
    except:
        return 1


def analyze_seniority_match(experience: List[Dict], requirements: str) -> Dict:
    try:
        total_years = calculate_total_experience_years(experience)

        if total_years >= 8:
            seniority_level = 'sênior'
            score = 90
        elif total_years >= 5:
            seniority_level = 'pleno'
            score = 75
        elif total_years >= 2:
            seniority_level = 'junior'
            score = 60
        else:
            seniority_level = 'estagiário'
            score = 40

        return {'score': score, 'level': seniority_level, 'years': total_years}
    except:
        return {'score': 0, 'level': 'unknown', 'years': 0}


def calculate_total_experience_years(experience: List[Dict]) -> int:
    try:
        if not isinstance(experience, list):
            return 0
        return sum(exp.get('years', 0) for exp in experience if isinstance(exp, dict))
    except:
        return 0


def extract_education_requirements(text: str) -> List[Dict]:
    """Extrai requisitos educacionais do texto"""
    requirements = []
    education_levels = {
        'mestrado': 'masters',
        'doutorado': 'phd',
        'graduação': 'bachelor',
        'tecnólogo': 'technologist',
        'técnico': 'technical'
    }

    for level_pt, level_en in education_levels.items():
        if level_pt in text.lower():
            requirements.append({'level': level_pt, 'type': level_en})

    return requirements


def analyze_experience_relevance(experience: List[Dict], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analisa relevância da experiência (implementação simplificada)"""
    try:
        # Verificar se há experiência relevante baseada no título do trabalho
        job_title = job_data.get('title', '').lower() if job_data else ''
        relevant_experience_count = 0

        if isinstance(experience, list):
            for exp in experience:
                if isinstance(exp, dict):
                    exp_title = exp.get('title', '').lower()
                    exp_description = exp.get('description', '').lower()

                    # Verificar se o título ou descrição contém palavras-chave do trabalho
                    if job_title and any(word in exp_title or word in exp_description for word in job_title.split()):
                        relevant_experience_count += 1

        total_experience = len(experience) if isinstance(experience, list) else 0
        score = (relevant_experience_count / max(total_experience, 1)) * 100 if total_experience > 0 else 50

        return {'score': min(score, 100)}
    except:
        return {'score': 50}


def analyze_experience_duration(experience: List[Dict], requirements: str) -> Dict[str, Any]:
    """Analisa duração da experiência (implementação simplificada)"""
    try:
        total_years = calculate_total_experience_years(experience)

        # Score baseado na duração total
        if total_years >= 5:
            score = 90
        elif total_years >= 3:
            score = 75
        elif total_years >= 1:
            score = 60
        else:
            score = 30

        return {'score': score}
    except:
        return {'score': 50}