import PyPDF2
import docx
import json
import re
import logging
from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class AdvancedResumeParser:
    def __init__(self):
        self.skills_database = self._load_comprehensive_skills_database()
        self.language_patterns = self._load_language_patterns()
        self.education_keywords = self._load_education_keywords()

    def _load_comprehensive_skills_database(self) -> Dict[str, List[str]]:
        """Banco de habilidades extremamente abrangente"""
        return {
            'technology': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin',
                'html', 'css', 'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js', 'express',
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server', 'sqlserver',
                'aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'terraform', 'jenkins', 'git', 'github',
                'pandas', 'numpy', 'tensorflow', 'pytorch', 'machine learning', 'deep learning', 'data science',
                'pyspark', 'spark', 'hadoop', 'hive', 'kafka', 'airflow', 'linux', 'bash', 'scala', 'r', 'matlab',
                'selenium', 'jira', 'confluence', 'grafana', 'splunk', 'elasticsearch', 'kibana',
                'power bi', 'tableau', 'excel', 'vba', 'macros', 'sas', 'jupyter', 'colab',
                'nlp', 'computer vision', 'neural networks', 'reinforcement learning',
                'etl', 'elt', 'data pipeline', 'data engineering', 'data warehouse', 'data lake',
                'big data', 'analytics', 'business intelligence', 'bi', 'api', 'rest', 'soap'
            ],

            'data_science': [
                'machine learning', 'deep learning', 'data science', 'data analysis', 'data analytics',
                'statistical analysis', 'predictive modeling', 'regression', 'classification', 'clustering',
                'time series', 'natural language processing', 'nlp', 'computer vision', 'neural networks',
                'supervised learning', 'unsupervised learning', 'reinforcement learning', 'feature engineering',
                'model deployment', 'model evaluation', 'cross validation', 'hyperparameter tuning',
                'a/b testing', 'hypothesis testing', 'data mining', 'pattern recognition',
                'data visualization', 'statistical modeling', 'quantitative analysis', 'clusterização',
                'regressão linear', 'regressão logística', 'séries temporais', 'modelagem preditiva'
            ],

            'cloud_platforms': [
                'aws', 'amazon web services', 'azure', 'microsoft azure', 'google cloud', 'gcp',
                's3', 'ec2', 'lambda', 'rds', 'redshift', 'athena', 'emr', 'sagemaker', 'glue',
                'kubernetes', 'docker', 'terraform', 'cloudformation'
            ],

            'business_intelligence': [
                'power bi', 'tableau', 'qlik', 'looker', 'metabase', 'superset', 'redash',
                'dashboard', 'kpi', 'metric', 'reporting', 'data visualization', 'business analytics',
                'performance monitoring', 'operational intelligence', 'strategic planning'
            ],

            'finance': [
                'financial analysis', 'budgeting', 'forecasting', 'financial modeling', 'investment analysis',
                'risk management', 'treasury', 'cash flow', 'profitability', 'cost analysis',
                'financial reporting', 'gaap', 'ifrs', 'audit', 'compliance', 'internal controls',
                'mergers and acquisitions', 'valuation', 'portfolio management', 'análise financeira',
                'tesouraria', 'projeções financeiras', 'economias', 'lucro', 'monetização', 'finanças',
                'grandes contas', 'produtos de prazo', 'performance financeira', 'otimização de pricing'
            ],

            'project_management': [
                'project management', 'agile', 'scrum', 'kanban', 'waterfall', 'pmbok',
                'risk assessment', 'stakeholder management', 'resource allocation', 'timeline management',
                'budget management', 'project planning', 'project execution', 'project monitoring',
                'change management', 'quality assurance', 'delivery management', 'gestão de projetos'
            ],

            'soft_skills': [
                'leadership', 'team management', 'communication', 'problem solving', 'critical thinking',
                'analytical thinking', 'strategic planning', 'decision making', 'negotiation',
                'collaboration', 'adaptability', 'creativity', 'innovation', 'time management',
                'conflict resolution', 'emotional intelligence', 'presentation skills',
                'proativo', 'colaborativo', 'comunicativo', 'liderança', 'gestão de equipe'
            ],

            'operations': [
                'gestão de frota', 'otimização', 'sazonalidade', 'demanda prevista', 'distribuição',
                'implantação', 'monitoramento de mercado', 'concorrência', 'alocação de recursos',
                'eficiência operacional', 'automação de processos', 'otimização de recursos'
            ],

            'languages': [
                'portuguese', 'english', 'spanish', 'french', 'german', 'italian', 'mandarin',
                'japanese', 'korean', 'russian', 'arabic', 'hindi'
            ]
        }

    def _load_language_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Padrões de regex para múltiplos idiomas"""
        return {
            'pt': {
                'name': r'^([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+)+)$',
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'phone': r'(\+55\s?)?(\(?\d{2}\)?[\s-]?)?(\d{4,5}[\s-]?\d{4})',
                'education_keywords': ['formação', 'educação', 'acadêmico', 'graduação', 'mestrado', 'doutorado',
                                       'curso', 'faculdade', 'universidade', 'especialização', 'MBA', 'bacharel'],
                'experience_keywords': ['experiência', 'profissional', 'empresa', 'trabalho', 'cargo', 'emprego',
                                        'atuação', 'carreira', 'profissão'],
                'skill_keywords': ['habilidades', 'competências', 'conhecimentos', 'skills', 'capacidades'],
            },
            'en': {
                'name': r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$',
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'phone': r'(\+1\s?)?(\(?\d{3}\)?[\s-]?)?(\d{3}[\s-]?\d{4})',
                'education_keywords': ['education', 'academic', 'degree', 'graduation', 'master', 'phd',
                                       'course', 'college', 'university', 'specialization', 'MBA', 'bachelor'],
                'experience_keywords': ['experience', 'professional', 'company', 'work', 'job', 'employment',
                                        'career', 'occupation'],
                'skill_keywords': ['skills', 'competencies', 'knowledge', 'abilities', 'capabilities'],
            },
            'es': {
                'name': r'^([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+)+)$',
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'phone': r'(\+34\s?)?(\(?\d{2}\)?[\s-]?)?(\d{4}[\s-]?\d{3})',
                'education_keywords': ['formación', 'educación', 'académico', 'grado', 'master', 'doctorado',
                                       'curso', 'facultad', 'universidad', 'especialización', 'MBA', 'bachiller'],
                'experience_keywords': ['experiencia', 'profesional', 'empresa', 'trabajo', 'cargo', 'empleo',
                                        'carrera', 'ocupación'],
                'skill_keywords': ['habilidades', 'competencias', 'conocimientos', 'capacidades'],
            }
        }

    def _load_education_keywords(self) -> List[str]:
        """Palavras-chave para identificar seção de educação"""
        return [
            'education', 'academic', 'degree', 'graduation', 'master', 'phd', 'course', 'college',
            'university', 'specialization', 'mba', 'bachelor', 'licentiate', 'doctorate',
            'formação', 'acadêmico', 'graduação', 'mestrado', 'doutorado', 'curso', 'faculdade',
            'universidade', 'especialização', 'bacharel', 'licenciatura', 'pós-graduação'
        ]

    def detect_language(self, text: str) -> str:
        """Detecta o idioma do texto com alta precisão"""
        if not text:
            return 'pt'

        text_lower = text.lower()

        # Palavras características por idioma
        language_indicators = {
            'pt': ['de', 'da', 'do', 'os', 'as', 'um', 'uma', 'é', 'são', 'para', 'com', 'não', 'mais'],
            'es': ['el', 'la', 'los', 'las', 'un', 'una', 'es', 'son', 'para', 'con', 'no', 'más'],
            'en': ['the', 'of', 'and', 'to', 'a', 'in', 'is', 'that', 'for', 'with', 'not', 'more']
        }

        scores = {lang: 0 for lang in language_indicators}

        words = text_lower.split()
        for word in words:
            for lang, indicators in language_indicators.items():
                if word in indicators:
                    scores[lang] += 1

        # Verifica padrões específicos
        for lang, patterns in self.language_patterns.items():
            for keyword in patterns['education_keywords']:
                if keyword in text_lower:
                    scores[lang] += 2

        return max(scores.items(), key=lambda x: x[1])[0] if max(scores.values()) > 0 else 'en'

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Processa currículo com tratamento robusto de erro"""
        try:
            file_ext = file_path.lower().split('.')[-1]

            if file_ext == 'pdf':
                text = self._extract_text_from_pdf(file_path)
            elif file_ext in ['doc', 'docx']:
                text = self._extract_text_from_docx(file_path)
            else:
                raise ValueError(f"Formato não suportado: {file_ext}")

            return self._advanced_extraction(text)

        except Exception as e:
            logger.error(f"Erro ao processar currículo {file_path}: {str(e)}")
            return self._get_fallback_resume_data()

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extrai texto de PDF com múltiplas estratégias"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"

            return text
        except Exception as e:
            logger.error(f"Erro PDF: {str(e)}")
            return ""

    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extrai texto de DOCX"""
        try:
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Erro DOCX: {str(e)}")
            return ""

    def _advanced_extraction(self, text: str) -> Dict[str, Any]:
        """Extrai informações usando técnicas avançadas"""
        if not text.strip():
            return self._get_fallback_resume_data()

        language = self.detect_language(text)
        patterns = self.language_patterns[language]

        # Limpa e normaliza texto
        text = re.sub(r'\s+', ' ', text)
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        info = {
            'personal_info': self._extract_personal_info_advanced(lines, patterns, language),
            'education': self._extract_education_advanced(lines, patterns, language),
            'experience': self._extract_experience_advanced(lines, patterns, language),
            'skills': self._extract_skills_advanced(text, language),
            'languages': self._extract_languages_advanced(text, language),
            'certifications': self._extract_certifications_advanced(text, language),
            'summary': self._extract_summary_advanced(lines, patterns, language),
            'raw_text': text,
            'detected_language': language,
            'area_detected': self._detect_primary_area_advanced(text, language)
        }

        return info

    def _extract_personal_info_advanced(self, lines: List[str], patterns: Dict, language: str) -> Dict[str, str]:
        """Extrai informações pessoais com técnicas avançadas - CORRIGIDA"""
        personal_info = {}

        # Procura primeiro por padrões específicos de contato
        full_text = ' '.join(lines)

        # Extrai email
        email_match = re.search(patterns['email'], full_text)
        if email_match:
            personal_info['email'] = email_match.group(0)

        # Extrai telefone
        phone_match = re.search(patterns['phone'], full_text)
        if phone_match:
            personal_info['phone'] = phone_match.group(0)

        # Procura LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9\-]+'
        linkedin_match = re.search(linkedin_pattern, full_text)
        if linkedin_match:
            personal_info['linkedin'] = 'https://' + linkedin_match.group(0)

        # Procura nome (geralmente nas primeiras linhas, após remover contatos)
        for i, line in enumerate(lines[:10]):
            # Remove informações de contato já encontradas
            clean_line = line
            if 'email' in personal_info:
                clean_line = clean_line.replace(personal_info['email'], '')
            if 'phone' in personal_info:
                clean_line = clean_line.replace(personal_info['phone'], '')

            # Verifica se é um nome válido
            if (re.match(patterns['name'], clean_line.strip()) and
                    len(clean_line.strip().split()) >= 2 and
                    len(clean_line.strip()) > 5):
                personal_info['name'] = clean_line.strip()
                break

        # Extrai localização (linhas iniciais que não são nome, email, telefone)
        location_candidates = []
        for i, line in enumerate(lines[:6]):
            clean_line = line.strip()
            # Remove informações já identificadas
            if 'name' in personal_info and personal_info['name'] in clean_line:
                clean_line = clean_line.replace(personal_info['name'], '')
            if 'email' in personal_info and personal_info['email'] in clean_line:
                clean_line = clean_line.replace(personal_info['email'], '')
            if 'phone' in personal_info and personal_info['phone'] in clean_line:
                clean_line = clean_line.replace(personal_info['phone'], '')

            # Verifica se pode ser uma localização
            if (clean_line and
                    len(clean_line) > 3 and
                    len(clean_line) < 100 and
                    not re.match(patterns['email'], clean_line) and
                    not re.match(patterns['phone'], clean_line) and
                    ('name' not in personal_info or personal_info['name'] not in line)):
                location_candidates.append(clean_line)

        # Pega a primeira linha candidata como localização
        if location_candidates:
            personal_info['location'] = location_candidates[0]

        # Se não encontrou nome, tenta encontrar no texto completo
        if 'name' not in personal_info:
            # Procura por padrões de nome em todo o texto
            words = full_text.split()
            for i in range(len(words) - 1):
                potential_name = f"{words[i]} {words[i + 1]}"
                if (re.match(patterns['name'], potential_name) and
                        len(potential_name.split()) >= 2):
                    personal_info['name'] = potential_name
                    break

        return personal_info

    def _extract_education_advanced(self, lines: List[str], patterns: Dict, language: str) -> List[Dict]:
        """Extrai seção de educação com maior precisão"""
        education = []
        in_education_section = False
        education_lines = []

        # Encontra a seção de educação
        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Detecta início da seção
            if any(keyword in line_lower for keyword in patterns['education_keywords']):
                in_education_section = True
                continue

            if in_education_section:
                # Para quando encontrar próxima seção principal
                if any(keyword in line_lower for keyword in
                       patterns['experience_keywords'] + patterns['skill_keywords'] + ['certificações',
                                                                                       'certifications', 'idiomas',
                                                                                       'languages']):
                    break

                if line.strip():
                    education_lines.append(line)

        # Processa as linhas de educação
        current_item = None
        for line in education_lines:
            # Verifica se é um novo item de educação (contém datas)
            date_pattern = r'\b(\d{4})\s*[-–]\s*(\d{4}|presente|atual)\b|\b(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|presente|atual)\b'
            date_match = re.search(date_pattern, line, re.IGNORECASE)

            if date_match:
                if current_item:
                    education.append(current_item)
                current_item = {
                    'date': date_match.group(0),
                    'description': re.sub(date_pattern, '', line).strip(),
                    'type': 'education'
                }
            elif current_item:
                # Continua a descrição do item atual
                current_item['description'] += ' ' + line.strip()

        if current_item:
            education.append(current_item)

        return education if education else [{'description': 'Educação não identificada', 'type': 'unknown'}]

    def _extract_experience_advanced(self, lines: List[str], patterns: Dict, language: str) -> List[Dict]:
        """Extrai seção de experiência profissional com maior precisão"""
        experience = []
        in_experience_section = False
        experience_lines = []

        # Encontra a seção de experiência
        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Detecta início da seção
            if any(keyword in line_lower for keyword in patterns['experience_keywords']):
                in_experience_section = True
                continue

            if in_experience_section:
                # Para quando encontrar próxima seção principal
                if any(keyword in line_lower for keyword in
                       patterns['education_keywords'] + patterns['skill_keywords'] + ['habilidades', 'skills',
                                                                                      'formação', 'education']):
                    break

                if line.strip():
                    experience_lines.append(line)

        # Processa as linhas de experiência
        current_item = None
        for line in experience_lines:
            # Verifica se é um novo item de experiência (contém datas)
            date_pattern = r'\b(\d{4})\s*[-–]\s*(\d{4}|presente|atual)\b|\b(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|presente|atual)\b'
            date_match = re.search(date_pattern, line, re.IGNORECASE)

            if date_match:
                if current_item:
                    experience.append(current_item)
                current_item = {
                    'date': date_match.group(0),
                    'description': re.sub(date_pattern, '', line).strip(),
                    'type': 'experience'
                }
            elif current_item:
                # Continua a descrição do item atual
                current_item['description'] += ' ' + line.strip()

        if current_item:
            experience.append(current_item)

        return experience if experience else [{'description': 'Experiência não identificada', 'type': 'unknown'}]

    def _extract_skills_advanced(self, text: str, language: str) -> List[Dict]:
        """Extrai habilidades com matching avançado"""
        skills = []
        text_lower = text.lower()

        for area, area_skills in self.skills_database.items():
            for skill in area_skills:
                # Verifica variações do skill em diferentes idiomas
                skill_variations = self._get_skill_variations_advanced(skill, language)

                for variation in skill_variations:
                    if variation.lower() in text_lower:
                        skills.append({
                            'name': skill,
                            'area': area,
                            'variation_found': variation,
                            'confidence': self._calculate_skill_confidence_advanced(text, variation)
                        })
                        break  # Evita duplicatas

        return skills

    def _get_skill_variations_advanced(self, skill: str, language: str) -> List[str]:
        """Retorna variações de skill por idioma"""
        variations_map = {
            'project management': {
                'pt': ['gestão de projetos', 'gerenciamento de projetos'],
                'es': ['gestión de proyectos'],
                'en': ['project management']
            },
            'team leadership': {
                'pt': ['liderança de equipe', 'liderança de time'],
                'es': ['liderazgo de equipo'],
                'en': ['team leadership', 'leadership']
            },
            'data science': {
                'pt': ['ciência de dados', 'data science'],
                'es': ['ciencia de datos'],
                'en': ['data science']
            },
            'machine learning': {
                'pt': ['aprendizado de máquina', 'machine learning'],
                'es': ['aprendizaje automático'],
                'en': ['machine learning']
            }
        }

        if skill in variations_map:
            return variations_map[skill].get(language, [skill])
        return [skill]

    def _calculate_skill_confidence_advanced(self, text: str, skill: str) -> float:
        """Calcula confiança na detecção da skill"""
        confidence = 0.5  # Base

        # Aumenta confiança se skill estiver em contexto relevante
        context_indicators = ['experiência em', 'conhecimento em', 'domínio de', 'proficiente em', 'skills in']
        for indicator in context_indicators:
            if f"{indicator} {skill}" in text.lower():
                confidence += 0.3

        # Aumenta confiança se skill for mencionada múltiplas vezes
        count = text.lower().count(skill.lower())
        confidence += min(count * 0.1, 0.2)

        return min(confidence, 1.0)

    def _extract_languages_advanced(self, text: str, language: str) -> List[Dict]:
        """Extrai idiomas mencionados com maior precisão"""
        language_map = {
            'pt': ['português', 'inglês', 'espanhol', 'francês', 'alemão', 'italiano', 'japonês', 'chinês'],
            'en': ['portuguese', 'english', 'spanish', 'french', 'german', 'italian', 'japanese', 'chinese'],
            'es': ['portugués', 'inglés', 'español', 'francés', 'alemán', 'italiano', 'japonés', 'chino']
        }

        languages = []
        text_lower = text.lower()

        for lang in language_map.get(language, language_map['en']):
            if lang in text_lower:
                # Tenta detectar nível de proficiência
                proficiency = self._detect_language_proficiency_advanced(text, lang, language)
                languages.append({
                    'language': lang,
                    'proficiency': proficiency
                })

        return languages

    def _detect_language_proficiency_advanced(self, text: str, language: str, doc_language: str) -> str:
        """Detecta nível de proficiência no idioma"""
        proficiency_indicators = {
            'pt': {
                'nativo': ['nativo', 'língua materna'],
                'fluente': ['fluente', 'avançado', 'proficiente'],
                'intermediário': ['intermediário', 'intermedio'],
                'básico': ['básico', 'iniciante', 'principiante']
            },
            'en': {
                'native': ['native', 'mother tongue'],
                'fluent': ['fluent', 'advanced', 'proficient'],
                'intermediate': ['intermediate'],
                'basic': ['basic', 'beginner']
            },
            'es': {
                'nativo': ['nativo', 'lengua materna'],
                'fluente': ['fluido', 'avanzado', 'competente'],
                'intermedio': ['intermedio'],
                'básico': ['básico', 'principiante']
            }
        }

        indicators = proficiency_indicators.get(doc_language, proficiency_indicators['en'])
        text_lower = text.lower()

        for level, level_indicators in indicators.items():
            for indicator in level_indicators:
                if indicator in text_lower and language in text_lower:
                    return level

        return 'not specified'

    def _extract_certifications_advanced(self, text: str, language: str) -> List[str]:
        """Extrai certificações mencionadas"""
        certifications = []
        cert_patterns = {
            'pt': ['certificação', 'certificado', 'curso', 'formação', 'treinamento'],
            'en': ['certification', 'certificate', 'course', 'training'],
            'es': ['certificación', 'certificado', 'curso', 'formación']
        }

        lines = text.split('\n')
        in_cert_section = False

        for line in lines:
            line_lower = line.lower()

            if any(keyword in line_lower for keyword in cert_patterns[language]):
                in_cert_section = True
                continue

            if in_cert_section and len(line.strip()) > 5:
                certifications.append(line.strip())

        return certifications

    def _extract_summary_advanced(self, lines: List[str], patterns: Dict, language: str) -> str:
        """Extrai resumo profissional"""
        summary_lines = []

        # Procura por parágrafo introdutório (geralmente no início, após informações pessoais)
        personal_info_found = False
        for i, line in enumerate(lines):
            if len(line) > 30 and not any(keyword in line.lower() for keyword in
                                          patterns['experience_keywords'] +
                                          patterns['education_keywords'] +
                                          patterns['skill_keywords']):
                if not personal_info_found:
                    # Verifica se é informação pessoal
                    if (re.search(patterns['email'], line) or
                            re.search(patterns['phone'], line) or
                            'linkedin' in line.lower()):
                        personal_info_found = True
                        continue

                summary_lines.append(line)
                if len(summary_lines) >= 2:  # Limita a 2 linhas para o resumo
                    break

        return ' '.join(summary_lines) if summary_lines else 'Resumo não identificado'

    def _detect_primary_area_advanced(self, text: str, language: str) -> str:
        """Detecta a área profissional principal com maior precisão"""
        area_scores = {}
        text_lower = text.lower()

        for area, skills in self.skills_database.items():
            score = 0
            for skill in skills:
                if skill in text_lower:
                    score += 1
                    # Skills mais específicos têm peso maior
                    if len(skill.split()) > 1:
                        score += 0.5

            if score > 0:
                area_scores[area] = score

        return max(area_scores.items(), key=lambda x: x[1])[0] if area_scores else 'general'

    def _parse_education_line_advanced(self, line: str, language: str) -> Dict:
        """Analisa linha de educação extraindo datas e descrição"""
        # Padrões de data
        date_pattern = r'(\d{4}\s*[-–]\s*\d{4}|\d{4}\s*[-–]\s*(?:presente|atual)|\w+\s+de\s+\d{4}\s*[-–]\s*\w+\s+de\s+\d{4})'
        date_match = re.search(date_pattern, line)

        date = date_match.group(0) if date_match else ''
        description = re.sub(date_pattern, '', line).strip()

        if description:
            return {
                'date': date,
                'description': description,
                'type': 'education'
            }
        return None

    def _parse_experience_line_advanced(self, line: str, language: str) -> Dict:
        """Analisa linha de experiência extraindo datas e descrição"""
        # Padrões de data mais flexíveis
        date_pattern = r'(\d{4}\s*[-–]\s*\d{4}|\d{4}\s*[-–]\s*(?:presente|atual)|\w+\s+de\s+\d{4}\s*[-–]\s*\w+\s+de\s+\d{4}|\d{1,2}/\d{4})'
        date_match = re.search(date_pattern, line)

        date = date_match.group(0) if date_match else ''
        description = re.sub(date_pattern, '', line).strip()

        if description:
            return {
                'date': date,
                'description': description,
                'type': 'experience'
            }
        return None

    def _get_fallback_resume_data(self) -> Dict[str, Any]:
        """Dados fallback quando extração falha"""
        return {
            'personal_info': {'name': 'Nome não identificado'},
            'education': [{'description': 'Educação não identificada', 'type': 'unknown'}],
            'experience': [{'description': 'Experiência não identificada', 'type': 'unknown'}],
            'skills': [],
            'languages': [],
            'certifications': [],
            'summary': 'Resumo não identificado',
            'raw_text': '',
            'detected_language': 'pt',
            'area_detected': 'general'
        }


# Função de interface para compatibilidade
def parse_resume(file_path: str) -> Dict[str, Any]:
    parser = AdvancedResumeParser()
    return parser.parse_resume(file_path)