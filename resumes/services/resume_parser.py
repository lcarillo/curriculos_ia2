import PyPDF2
import docx
import json
import re
import logging
from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher
import dateutil.parser as dparser
from datetime import datetime
import spacy
from spacy.matcher import Matcher, PhraseMatcher

logger = logging.getLogger(__name__)


class AdvancedResumeParser:
    def __init__(self):
        self.skills_database = self._load_comprehensive_skills_database()
        self.language_patterns = self._load_language_patterns()
        self.education_keywords = self._load_education_keywords()
        self.experience_keywords = self._load_experience_keywords()
        self.nlp_models = {}

    def _load_spacy_model(self, language: str):
        """Carrega modelos spaCy para diferentes idiomas"""
        if language not in self.nlp_models:
            models = {
                'pt': 'pt_core_news_sm',
                'en': 'en_core_web_sm',
                'es': 'es_core_news_sm'
            }
            try:
                self.nlp_models[language] = spacy.load(models[language])
            except OSError:
                logger.warning(f"Modelo spaCy {models[language]} não encontrado, usando regex apenas")
                self.nlp_models[language] = None
        return self.nlp_models[language]

    def _load_comprehensive_skills_database(self) -> Dict[str, List[str]]:
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
            'marketing': [
                'marketing digital', 'seo', 'sem', 'google ads', 'facebook ads', 'instagram ads',
                'google analytics', 'redes sociais', 'social media', 'copywriting', 'e-mail marketing',
                'content marketing', 'inbound marketing', 'outbound marketing', 'branding',
                'publicidade', 'comunicação', 'mídia paga', 'analytics', 'kpi', 'roi',
                'gestão de tráfego', 'campanhas digitais', 'marketing de conteúdo', 'lead generation',
                'conversão', 'funil de vendas', 'customer journey', 'personas', 'segmentação',
                'engajamento', 'orgânico', 'paid media', 'metas', 'estratégia de marketing',
                'planejamento estratégico', 'pesquisa de mercado', 'competitive analysis',
                'brand awareness', 'crm', 'marketing automation', 'salesforce', 'hubspot'
            ],
            'sales': [
                'vendas', 'sales', 'negociação', 'prospecção', 'fechamento', 'funil de vendas',
                'gestão de carteira', 'relacionamento com cliente', 'customer success',
                'metas comerciais', 'apresentação comercial', 'proposta comercial'
            ],
            'languages': [
                'portuguese', 'english', 'spanish', 'french', 'german', 'italian', 'mandarin',
                'japanese', 'korean', 'russian', 'arabic', 'hindi'
            ]
        }

    def _load_language_patterns(self) -> Dict[str, Dict[str, Any]]:
        return {
            'pt': {
                'name': r'^([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+)+)$',
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'phone': r'(\+55\s?)?(\(?\d{2}\)?[\s-]?)?(\d{4,5}[\s-]?\d{4})',
                'education_keywords': ['formação', 'educação', 'acadêmico', 'graduação', 'mestrado', 'doutorado',
                                       'curso', 'faculdade', 'universidade', 'especialização', 'MBA', 'bacharel',
                                       'ensino', 'acadêmica', 'escolaridade', 'formação acadêmica'],
                'experience_keywords': ['experiência', 'profissional', 'empresa', 'trabalho', 'cargo', 'emprego',
                                        'atuação', 'carreira', 'profissão', 'experiencia', 'histórico profissional',
                                        'histórico de trabalho', 'histórico de emprego', 'experiências profissionais'],
                'skill_keywords': ['habilidades', 'competências', 'conhecimentos', 'skills', 'capacidades',
                                   'ferramentas', 'tecnologias', 'qualificações'],
                'summary_keywords': ['resumo', 'perfil', 'objetivo', 'sobre', 'profile', 'summary'],
                'language_keywords': ['idiomas', 'línguas', 'idioma', 'língua'],
                'certification_keywords': ['certificações', 'cursos', 'certificados', 'certificado', 'certificação'],
            },
            'en': {
                'name': r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$',
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'phone': r'(\+1\s?)?(\(?\d{3}\)?[\s-]?)?(\d{3}[\s-]?\d{4})',
                'education_keywords': ['education', 'academic', 'degree', 'graduation', 'master', 'phd',
                                       'course', 'college', 'university', 'specialization', 'MBA', 'bachelor',
                                       'studies', 'academic background', 'qualifications'],
                'experience_keywords': ['experience', 'professional', 'company', 'work', 'job', 'employment',
                                        'career', 'occupation', 'work experience', 'employment history',
                                        'professional experience'],
                'skill_keywords': ['skills', 'competencies', 'knowledge', 'abilities', 'capabilities',
                                   'tools', 'technologies', 'qualifications'],
                'summary_keywords': ['summary', 'profile', 'objective', 'about', 'professional summary'],
                'language_keywords': ['languages', 'language'],
                'certification_keywords': ['certifications', 'courses', 'certificates', 'certification'],
            },
            'es': {
                'name': r'^([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+)+)$',
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'phone': r'(\+34\s?)?(\(?\d{2}\)?[\s-]?)?(\d{4}[\s-]?\d{3})',
                'education_keywords': ['formación', 'educación', 'académico', 'grado', 'master', 'doctorado',
                                       'curso', 'facultad', 'universidad', 'especialización', 'MBA', 'bachiller',
                                       'estudios', 'formación académica'],
                'experience_keywords': ['experiencia', 'profesional', 'empresa', 'trabajo', 'cargo', 'empleo',
                                        'carrera', 'ocupación', 'experiencia laboral', 'historial laboral'],
                'skill_keywords': ['habilidades', 'competencias', 'conocimientos', 'capacidades',
                                   'herramientas', 'tecnologías', 'cualificaciones'],
                'summary_keywords': ['resumen', 'perfil', 'objetivo', 'sobre'],
                'language_keywords': ['idiomas', 'lenguas', 'idioma', 'lengua'],
                'certification_keywords': ['certificaciones', 'cursos', 'certificados', 'certificación'],
            }
        }

    def _load_education_keywords(self) -> List[str]:
        return [
            'education', 'academic', 'degree', 'graduation', 'master', 'phd', 'course', 'college',
            'university', 'specialization', 'mba', 'bachelor', 'licentiate', 'doctorate',
            'formação', 'acadêmico', 'graduação', 'mestrado', 'doutorado', 'curso', 'faculdade',
            'universidade', 'especialização', 'bacharel', 'licenciatura', 'pós-graduação',
            'formación', 'educación', 'grado', 'master', 'doctorado', 'facultad', 'universidad'
        ]

    def _load_experience_keywords(self) -> List[str]:
        return [
            'experience', 'professional', 'company', 'work', 'job', 'employment', 'career',
            'occupation', 'work experience', 'employment history', 'professional experience',
            'experiência', 'profissional', 'empresa', 'trabalho', 'cargo', 'emprego', 'carreira',
            'experiencia', 'profesional', 'trabajo', 'empleo', 'carrera'
        ]

    def detect_language(self, text: str) -> str:
        if not text:
            return 'pt'

        text_lower = text.lower()
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

        for lang, patterns in self.language_patterns.items():
            for keyword_category in ['education_keywords', 'experience_keywords']:
                for keyword in patterns[keyword_category]:
                    if keyword in text_lower:
                        scores[lang] += 2

        return max(scores.items(), key=lambda x: x[1])[0] if max(scores.values()) > 0 else 'en'

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
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
        try:
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Erro DOCX: {str(e)}")
            return ""

    def _advanced_extraction(self, text: str) -> Dict[str, Any]:
        if not text.strip():
            return self._get_fallback_resume_data()

        language = self.detect_language(text)
        patterns = self.language_patterns[language]
        nlp = self._load_spacy_model(language)

        text = re.sub(r'\s+', ' ', text)
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        info = {
            'personal_info': self._extract_personal_info_advanced(lines, patterns, language, nlp),
            'education': self._extract_education_advanced(lines, patterns, language, nlp),
            'experience': self._extract_experience_advanced(lines, patterns, language, nlp),
            'skills': self._extract_skills_advanced(text, language, nlp),
            'languages': self._extract_languages_advanced(text, language),
            'certifications': self._extract_certifications_advanced(text, language),
            'projects': self._extract_projects_advanced(text, language),
            'soft_skills': self._extract_soft_skills_advanced(text, language),
            'summary': self._extract_summary_advanced(lines, patterns, language),
            'raw_text': text,
            'detected_language': language,
            'area_detected': self._detect_primary_area_advanced(text, language)
        }

        return info

    def _extract_personal_info_advanced(self, lines: List[str], patterns: Dict, language: str, nlp) -> Dict[str, str]:
        personal_info = {}
        full_text = ' '.join(lines)

        email_match = re.search(patterns['email'], full_text)
        if email_match:
            personal_info['email'] = email_match.group(0)

        phone_match = re.search(patterns['phone'], full_text)
        if phone_match:
            personal_info['phone'] = phone_match.group(0)

        linkedin_patterns = [
            r'linkedin\.com/in/[a-zA-Z0-9\-]+',
            r'linkedin\.com/[a-zA-Z0-9\-]+',
            r'linkedin/[a-zA-Z0-9\-]+'
        ]
        for pattern in linkedin_patterns:
            linkedin_match = re.search(pattern, full_text.lower())
            if linkedin_match:
                linkedin_url = linkedin_match.group(0)
                if not linkedin_url.startswith('http'):
                    linkedin_url = 'https://' + linkedin_url
                personal_info['linkedin'] = linkedin_url
                break

        if nlp:
            doc = nlp(full_text)
            for ent in doc.ents:
                if ent.label_ == "PER":
                    personal_info['name'] = ent.text
                    break

        if 'name' not in personal_info:
            for i, line in enumerate(lines[:8]):
                clean_line = line.strip()
                if 'email' in personal_info:
                    clean_line = clean_line.replace(personal_info['email'], '')
                if 'phone' in personal_info:
                    clean_line = clean_line.replace(personal_info['phone'], '')

                words = clean_line.split()
                if (len(words) >= 2 and
                        all(len(word) > 1 and word[0].isupper() for word in words if word) and
                        len(clean_line) > 5 and len(clean_line) < 100 and
                        not any(keyword in clean_line.lower() for keyword in
                                patterns['education_keywords'] +
                                patterns['experience_keywords'] +
                                patterns['skill_keywords'])):
                    personal_info['name'] = clean_line
                    break

        location_patterns = [
            r'([A-Z][a-z]+(?:[\s-]+[A-Z][a-z]+)*\s*,\s*[A-Z]{2})',
            r'([A-Z][a-z]+(?:[\s-]+[A-Z][a-z]+)*\s*-\s*[A-Z]{2})',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]

        for pattern in location_patterns:
            location_match = re.search(pattern, full_text)
            if location_match:
                location = location_match.group(0).strip()
                if (len(location) > 3 and
                        len(location) < 50 and
                        ('name' not in personal_info or personal_info['name'] not in location)):
                    personal_info['location'] = location
                    break

        return personal_info

    def _extract_education_advanced(self, lines: List[str], patterns: Dict, language: str, nlp) -> List[Dict]:
        education = []
        education_sections = []
        current_section = []

        sentences = [sent.text for sent in nlp(' '.join(lines)).sents] if nlp else lines
        education_keywords = patterns['education_keywords']

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in education_keywords):
                if current_section:
                    education_sections.append(" ".join(current_section))
                    current_section = []
                current_section.append(sentence)
            elif current_section:
                current_section.append(sentence)

        if current_section:
            education_sections.append(" ".join(current_section))

        return self._parse_education_details(education_sections, language, nlp)

    def _parse_education_details(self, sections: List[str], language: str, nlp) -> List[Dict]:
        educations = []
        date_pattern = r'(\d{1,2}[/-]\d{4}|\d{4})'

        for section in sections:
            doc_section = nlp(section) if nlp else None
            education = {
                'degree': '',
                'institution': '',
                'year': '',
                'description': section,
                'type': 'education'
            }

            dates = re.findall(date_pattern, section)
            if dates:
                education['year'] = dates[-1]

            if doc_section:
                for ent in doc_section.ents:
                    if ent.label_ == "ORG":
                        education['institution'] = ent.text
                        break

            educations.append(education)
        return educations if educations else [{'description': 'Educação não identificada', 'type': 'unknown'}]

    def _extract_experience_advanced(self, lines: List[str], patterns: Dict, language: str, nlp) -> List[Dict]:
        experience = []
        experience_sections = []
        current_section = []

        sentences = [sent.text for sent in nlp(' '.join(lines)).sents] if nlp else lines
        experience_keywords = patterns['experience_keywords']

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in experience_keywords):
                if current_section:
                    experience_sections.append(" ".join(current_section))
                    current_section = []
                current_section.append(sentence)
            elif current_section:
                current_section.append(sentence)

        if current_section:
            experience_sections.append(" ".join(current_section))

        return self._parse_experience_details(experience_sections, language, nlp)

    def _parse_experience_details(self, sections: List[str], language: str, nlp) -> List[Dict]:
        experiences = []
        date_pattern = r'(\d{1,2}[/-]\d{4}|\d{4})'

        for section in sections:
            doc_section = nlp(section) if nlp else None
            experience = {
                'position': '',
                'company': '',
                'duration': '',
                'description': section,
                'type': 'experience'
            }

            dates = re.findall(date_pattern, section)
            if len(dates) >= 2:
                experience['duration'] = f"{dates[0]} - {dates[1]}"
            elif dates:
                experience['duration'] = dates[0]

            if doc_section:
                for ent in doc_section.ents:
                    if ent.label_ == "ORG":
                        experience['company'] = ent.text
                    elif not experience['position']:
                        if ent.label_ in ["PER", "MISC"]:
                            experience['position'] = ent.text

            experiences.append(experience)
        return experiences if experiences else [{'description': 'Experiência não identificada', 'type': 'unknown'}]

    def _extract_skills_advanced(self, text: str, language: str, nlp) -> List[Dict]:
        skills = []
        text_lower = text.lower()

        for area, area_skills in self.skills_database.items():
            for skill in area_skills:
                skill_variations = self._get_skill_variations_advanced(skill, language)

                for variation in skill_variations:
                    if variation.lower() in text_lower:
                        if self._is_valid_skill_context(text, variation):
                            skills.append({
                                'name': skill,
                                'area': area,
                                'variation_found': variation,
                                'confidence': self._calculate_skill_confidence_advanced(text, variation)
                            })
                            break

        unique_skills = []
        seen_skills = set()
        for skill in skills:
            skill_key = skill['name'].lower()
            if skill_key not in seen_skills:
                unique_skills.append(skill)
                seen_skills.add(skill_key)

        return unique_skills

    def _get_skill_variations_advanced(self, skill: str, language: str) -> List[str]:
        variations_map = {
            'project management': {
                'pt': ['gestão de projetos', 'gerenciamento de projetos', 'gestao de projetos'],
                'es': ['gestión de proyectos'],
                'en': ['project management', 'project manager']
            },
            'team leadership': {
                'pt': ['liderança de equipe', 'liderança de time', 'gestão de equipe'],
                'es': ['liderazgo de equipo'],
                'en': ['team leadership', 'leadership', 'team lead']
            },
            'data science': {
                'pt': ['ciência de dados', 'data science', 'ciencia de dados'],
                'es': ['ciencia de datos'],
                'en': ['data science']
            },
            'machine learning': {
                'pt': ['aprendizado de máquina', 'machine learning', 'aprendizado de maquina'],
                'es': ['aprendizaje automático'],
                'en': ['machine learning', 'ml']
            }
        }

        if skill in variations_map:
            return variations_map[skill].get(language, [skill])
        return [skill]

    def _is_valid_skill_context(self, text: str, skill: str) -> bool:
        valid_contexts = [
            f'experiência em {skill}',
            f'conhecimento em {skill}',
            f'domínio de {skill}',
            f'proficiente em {skill}',
            f'habilidade em {skill}',
            f'skills in {skill}',
            f'competência em {skill}',
        ]

        text_lower = text.lower()
        for context in valid_contexts:
            if context in text_lower:
                return True

        if text_lower.count(skill.lower()) >= 2:
            return True

        return False

    def _calculate_skill_confidence_advanced(self, text: str, skill: str) -> float:
        confidence = 0.5
        context_indicators = ['experiência em', 'conhecimento em', 'domínio de', 'proficiente em', 'skills in']
        for indicator in context_indicators:
            if f"{indicator} {skill}" in text.lower():
                confidence += 0.3

        count = text.lower().count(skill.lower())
        confidence += min(count * 0.1, 0.2)

        return min(confidence, 1.0)

    def _extract_languages_advanced(self, text: str, language: str) -> List[Dict]:
        language_map = {
            'pt': ['português', 'inglês', 'espanhol', 'francês', 'alemão', 'italiano', 'japonês', 'chinês'],
            'en': ['portuguese', 'english', 'spanish', 'french', 'german', 'italian', 'japanese', 'chinese'],
            'es': ['portugués', 'inglés', 'español', 'francés', 'alemán', 'italiano', 'japonés', 'chino']
        }

        languages = []
        text_lower = text.lower()

        for lang in language_map.get(language, language_map['en']):
            if lang in text_lower:
                proficiency = self._detect_language_proficiency_advanced(text, lang, language)
                languages.append({
                    'language': lang,
                    'proficiency': proficiency
                })

        if not languages:
            languages = self._extract_languages_fallback(text, language)

        return languages

    def _detect_language_proficiency_advanced(self, text: str, language: str, doc_language: str) -> str:
        proficiency_indicators = {
            'pt': {
                'nativo': ['nativo', 'língua materna', 'materna'],
                'fluente': ['fluente', 'avançado', 'proficiente', 'fluente'],
                'intermediário': ['intermediário', 'intermedio', 'intermediario'],
                'básico': ['básico', 'iniciante', 'principiante', 'basico']
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

        language_index = text_lower.find(language)
        if language_index != -1:
            context_start = max(0, language_index - 50)
            context_end = min(len(text_lower), language_index + len(language) + 50)
            context = text_lower[context_start:context_end]

            for level, level_indicators in indicators.items():
                for indicator in level_indicators:
                    if indicator in context:
                        return level

        return 'not specified'

    def _extract_languages_fallback(self, text: str, language: str) -> List[Dict]:
        languages = []
        text_lower = text.lower()
        common_languages = ['português', 'inglês', 'espanhol', 'francês', 'alemão', 'italiano',
                            'portuguese', 'english', 'spanish', 'french', 'german', 'italian']

        for lang in common_languages:
            if lang in text_lower:
                languages.append({
                    'language': lang,
                    'proficiency': 'not specified'
                })

        return languages

    def _extract_certifications_advanced(self, text: str, language: str) -> List[Dict]:
        certifications = []
        lines = text.split('\n')

        for line in lines:
            line_clean = line.strip()
            if len(line_clean) > 10 and any(keyword in line_clean.lower() for keyword in
                                            ['certificado', 'certificação', 'certification', 'curso', 'course']):
                certifications.append({
                    'name': line_clean,
                    'type': 'certification'
                })

        return certifications

    def _extract_projects_advanced(self, text: str, language: str) -> List[Dict]:
        projects = []
        lines = text.split('\n')

        for line in lines:
            line_clean = line.strip()
            if (len(line_clean) > 15 and
                    any(keyword in line_clean.lower() for keyword in
                        ['projeto', 'project', 'portfólio', 'portfolio', 'trabalho', 'work'])):
                projects.append({
                    'name': line_clean,
                    'description': line_clean,
                    'type': 'project'
                })

        return projects

    def _extract_soft_skills_advanced(self, text: str, language: str) -> List[str]:
        soft_skills = []
        text_lower = text.lower()

        for skill in self.skills_database['soft_skills']:
            if skill in text_lower:
                soft_skills.append(skill)

        return list(set(soft_skills))

    def _extract_summary_advanced(self, lines: List[str], patterns: Dict, language: str) -> str:
        summary_lines = []
        in_summary_section = False

        for i, line in enumerate(lines):
            line_lower = line.lower()

            if any(keyword in line_lower for keyword in patterns['summary_keywords']):
                in_summary_section = True
                continue

            if in_summary_section:
                if any(keyword in line_lower for keyword in
                       patterns['experience_keywords'] + patterns['education_keywords']):
                    break

                if line.strip() and len(line.strip()) > 20:
                    summary_lines.append(line.strip())

        if not summary_lines:
            for i, line in enumerate(lines[:5]):
                if (len(line.strip()) > 30 and
                        not any(keyword in line.lower() for keyword in
                                patterns['experience_keywords'] + patterns['education_keywords'] +
                                patterns['skill_keywords']) and
                        not re.search(patterns['email'], line) and
                        not re.search(patterns['phone'], line)):
                    summary_lines.append(line.strip())
                    if len(summary_lines) >= 2:
                        break

        return ' '.join(summary_lines) if summary_lines else 'Resumo não identificado'

    def _detect_primary_area_advanced(self, text: str, language: str) -> str:
        area_scores = {}
        text_lower = text.lower()

        for area, skills in self.skills_database.items():
            if area == 'languages':
                continue

            score = 0
            for skill in skills:
                if skill in text_lower:
                    score += 1
                    if len(skill.split()) > 1:
                        score += 0.5

            if score > 0:
                area_scores[area] = score

        if not area_scores:
            area_keywords = {
                'technology': ['desenvolvedor', 'developer', 'programador', 'software', 'ti', 'tecnologia'],
                'marketing': ['marketing', 'mkt', 'publicidade', 'branding', 'seo', 'social media'],
                'finance': ['financeiro', 'finanças', 'contábil', 'contabilidade', 'financial'],
                'project_management': ['gerente de projetos', 'project manager', 'scrum master'],
                'data_science': ['cientista de dados', 'data scientist', 'analista de dados'],
            }

            for area, keywords in area_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        area_scores[area] = area_scores.get(area, 0) + 1

        return max(area_scores.items(), key=lambda x: x[1])[0] if area_scores else 'general'

    def _get_fallback_resume_data(self) -> Dict[str, Any]:
        return {
            'personal_info': {'name': 'Nome não identificado'},
            'education': [{'description': 'Educação não identificada', 'type': 'unknown'}],
            'experience': [{'description': 'Experiência não identificada', 'type': 'unknown'}],
            'skills': [],
            'languages': [],
            'certifications': [],
            'projects': [],
            'soft_skills': [],
            'summary': 'Resumo não identificado',
            'raw_text': '',
            'detected_language': 'pt',
            'area_detected': 'general'
        }


def parse_resume(file_path: str) -> Dict[str, Any]:
    parser = AdvancedResumeParser()
    return parser.parse_resume(file_path)