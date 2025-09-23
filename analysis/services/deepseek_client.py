import os
import json
import httpx
from typing import Dict, Any

class DeepSeekClient:
    def __init__(self):
        self.api_key = os.environ.get('DEEPSEEK_API_KEY')
        self.base_url = os.environ.get('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
        self.model = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')
        self.use_stub = not self.api_key

    def generate_suggestions(self, resume_data: Dict[str, Any], job_data: Dict[str, Any],
                             analysis_results: Dict[str, Any]) -> str:
        if self.use_stub:
            return self._generate_stub_suggestions(resume_data, job_data, analysis_results)

        prompt = self._build_suggestions_prompt(resume_data, job_data, analysis_results)
        return self._make_api_call(prompt)

    def optimize_resume(self, resume_data: Dict[str, Any], job_data: Dict[str, Any],
                        analysis_results: Dict[str, Any]) -> str:
        if self.use_stub:
            return self._generate_stub_optimized_resume(resume_data, job_data, analysis_results)

        prompt = self._build_optimize_prompt(resume_data, job_data, analysis_results)
        response = self._make_api_call(prompt)
        return self._validate_resume_length(response)

    def _make_api_call(self, prompt: str) -> str:
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': self.model,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.7,
                'max_tokens': 4000
            }

            with httpx.Client() as client:
                response = client.post(
                    f'{self.base_url}/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=60.0
                )
                response.raise_for_status()

                result = response.json()
                return result['choices'][0]['message']['content']

        except Exception as e:
            return f"Erro na API DeepSeek: {str(e)}. Usando sugestões simuladas."

    def _build_suggestions_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any],
                                  analysis_results: Dict[str, Any]) -> str:
        resume_json = json.dumps(resume_data, ensure_ascii=False, indent=2)
        job_json = json.dumps(job_data, ensure_ascii=False, indent=2)
        analysis_json = json.dumps(analysis_results, ensure_ascii=False, indent=2)

        return f"""
        Como especialista em recrutamento e otimização de currículos, analise os dados abaixo e forneça sugestões específicas e acionáveis.

        ANÁLISE DETALHADA DA COMPATIBILIDADE:
        {analysis_json}

        DADOS DO CURRÍCULO:
        {resume_json}

        DESCRIÇÃO DA VAGA:
        {job_json}

        COM BASE NA ANÁLISE ACIMA, FORNEÇA SUGESTÕES CONCRETAS PARA:

        1. OTIMIZAÇÃO DE HABILIDADES:
        - Quais habilidades faltantes são mais críticas para esta vaga?
        - Como destacar melhor as habilidades existentes que são relevantes?
        - Sugestões de reformulação para aumentar o impacto

        2. OTIMIZAÇÃO DE PALAVRAS-CHAVE:
        - Quais palavras-chave específicas devem ser adicionadas?
        - Como incorporá-las naturalmente no currículo?
        - Estratégias para aumentar a densidade de keywords relevantes

        3. OTIMIZAÇÃO DA EXPERIÊNCIA PROFISSIONAL:
        - Como reformular as descrições para destacar resultados?
        - Quais experiências devem ser priorizadas/reduzidas?
        - Sugestões de métricas e números para incluir

        4. ESTRUTURA E FORMATAÇÃO:
        - Melhorias na organização do conteúdo
        - Sugestões de ordem e hierarquia
        - Elementos visuais que podem aumentar a legibilidade

        FORMATO DA RESPOSTA:
        - Use tópicos claros e objetivos
        - Inclua exemplos concretos de reformulação
        - Priorize as sugestões por impacto potencial
        - Seja específico e acionável

        Forneça pelo menos 5 sugestões específicas para cada categoria.
        """

    def _build_optimize_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any],
                               analysis_results: Dict[str, Any]) -> str:
        resume_json = json.dumps(resume_data, ensure_ascii=False, indent=2)
        job_json = json.dumps(job_data, ensure_ascii=False, indent=2)
        analysis_json = json.dumps(analysis_results, ensure_ascii=False, indent=2)

        return f"""
        COMO ESPECIALISTA EM RECRUTAMENTO, OTIMIZE ESTE CURRÍCULO PARA A VAGA ESPECÍFICA, 
        MANTENDO NO MÁXIMO 2 PÁGINAS E FOCO NAS INFORMAÇÕES MAIS RELEVANTES.

        REGRAS ESTRITAS:
        - MÁXIMO DE 2 PÁGINAS (aproximadamente 800-1000 palavras)
        - Formato profissional e moderno
        - Foco absoluto nas competências relevantes para a vaga
        - Use verbos de ação e métricas mensuráveis
        - Seja conciso e direto ao ponto

        ANÁLISE DE COMPATIBILIDADE (use para priorizar conteúdo):
        {analysis_json}

        DADOS DO CURRÍCULO ORIGINAL:
        {resume_json}

        DESCRIÇÃO DA VAGA (foco principal):
        {job_json}

        ESTRUTURA OBRIGATÓRIA (2 páginas máximo):

        [CABEÇALHO - 1ª PÁGINA]
        **NOME COMPLETO** (16-18pt, negrito)
        Cidade, Estado | Telefone | Email | LinkedIn (se disponível)

        [RESUMO PROFISSIONAL - 4-5 linhas máximo]
        - Destaque como sua experiência se alinha PERFEITAMENTE com a vaga
        - Inclua as 3-4 principais competências relevantes
        - Use palavras-chave identificadas na análise

        [EXPERIÊNCIA PROFISSIONAL - priorize relevância]
        **Formato por experiência:**
        **Cargo** | Empresa | Período (ex: Jan 2020 - Presente)
        - Bullet points com FOCO EM RESULTADOS (máximo 4 por experiência)
        - Use números: "aumentou vendas em 30%", "reduziu custos em R$ 50k"
        - Destaque habilidades específicas da vaga
        - Remova experiências irrelevantes ou muito antigas

        [FORMAÇÃO ACADÊMICA - apenas informações principais]
        - Curso, Instituição, Ano de conclusão
        - Inclua apenas se relevante para a vaga

        [HABILIDADES TÉCNICAS - organizadas por relevância]
        Agrupe em categorias priorizando as mais relevantes para a vaga
        Exemplo: 
        **Linguagens de Programação:** Python, JavaScript, SQL
        **Ferramentas:** Git, Docker, AWS
        **Metodologias:** Agile, Scrum, DevOps

        [IDIOMAS E CERTIFICAÇÕES - apenas se relevantes]
        - Inclua apenas se mencionado na vaga ou for diferencial

        DIRETRIZES CRÍTICAS:
        1. PRIORIZE conteúdo que tenha alta relevância na análise de compatibilidade
        2. REMOVA experiências com baixa relevância para liberar espaço
        3. USE as palavras-chave identificadas na análise naturalmente
        4. DESTAQUE habilidades que são requisitos obrigatórios na vaga
        5. MANTENHA o layout limpo e profissional com espaçamento adequado
        6. GARANTA que caiba em 2 páginas verificando o comprimento

        Ao final, verifique se o currículo gerado tem aproximadamente 800-1000 palavras 
        e está otimizado para os sistemas de tracking de candidaturas (ATS).
        """

    def _validate_resume_length(self, resume_text: str) -> str:
        words = resume_text.split()
        if len(words) > 1000:
            sections = resume_text.split('\n\n')
            optimized_sections = []

            for section in sections:
                if len(section.split()) > 150:
                    lines = section.split('\n')
                    optimized_section = '\n'.join(lines[:8])
                    optimized_sections.append(optimized_section + "\n[... conteúdo resumido ...]")
                else:
                    optimized_sections.append(section)

            return '\n\n'.join(optimized_sections)

        return resume_text

    def _generate_stub_suggestions(self, resume_data: Dict[str, Any], job_data: Dict[str, Any],
                                   analysis_results: Dict[str, Any]) -> str:
        job_title = job_data.get('title', 'Desenvolvedor')
        company = job_data.get('company', 'a empresa')
        overall_score = analysis_results.get('overall_score', 0)

        skills_analysis = analysis_results.get('skills_analysis', {})
        missing_skills = skills_analysis.get('missing_skills', [])
        exact_matches = skills_analysis.get('exact_matches', [])

        missing_skill_names = [skill.get('name', '') for skill in missing_skills[:4]]
        matching_skill_names = [match.get('job_skill', {}).get('name', '') for match in exact_matches[:4]]

        keyword_analysis = analysis_results.get('keyword_analysis', {})
        missing_keywords = [kw.get('keyword', '') for kw in keyword_analysis.get('missing_keywords', [])[:5]]

        return f"""
    📊 **RELATÓRIO DE OTIMIZAÇÃO - MODO DEMONSTRAÇÃO**
    **Compatibilidade: {overall_score}%** | Vaga: {job_title} | Empresa: {company}

    🎯 **ANÁLISE DETALHADA DA COMPATIBILIDADE**

    **1. HABILIDADES TÉCNICAS** ({skills_analysis.get('score', 0)}% de compatibilidade)
    ✅ **Pontos fortes:** {', '.join(matching_skill_names) if matching_skill_names else 'Habilidades básicas identificadas'}
    📈 **Oportunidades:** {', '.join(missing_skill_names) if missing_skill_names else 'Todas as habilidades principais atendidas'}

    **2. PALAVRAS-CHAVE ESTRATÉGICAS** ({keyword_analysis.get('score', 0)}% de densidade)
    🔍 **Keywords faltantes:** {', '.join(missing_keywords) if missing_keywords else 'Boas palavras-chave identificadas'}

    💡 **SUGESTÕES ESPECÍFICAS DE MELHORIA**

    **A. OTIMIZAÇÃO DE HABILIDADES:**
    • Adicione seção dedicada para: {', '.join(missing_skill_names[:2]) if missing_skill_names else 'habilidades técnicas específicas'}
    • Destaque projetos que demonstrem experiência em {job_title.lower()}
    • Use verbos de ação: "desenvolvi", "implementei", "otimizei", "liderei"

    **B. PALAVRAS-CHAVE E ATS:**
    • Incorpore naturalmente: "{job_title}", "{company}", "{', '.join(missing_keywords[:3]) if missing_keywords else 'tecnologias relevantes'}"
    • Estruture com bullet points para melhor leitura por sistemas ATS
    • Use variações de keywords para cobrir diferentes termos de busca

    **C. EXPERIÊNCIA PROFISSIONAL:**
    • Reformule descrições focando em RESULTADOS mensuráveis
    • Adicione métricas: "aumentei eficiência em 30%", "reduzi custos em R$ 50k"
    • Priorize experiências mais relevantes para {job_title}

    **D. ESTRUTURA E FORMATAÇÃO:**
    • Mantenha máximo de 2 páginas
    • Use formatação limpa e profissional
    • Destaque certificações e cursos relevantes

    🚀 **PRÓXIMOS PASSOS RECOMENDADOS**
    1. Revise e ajuste as seções conforme as sugestões acima
    2. Teste o currículo em sistemas ATS online
    3. Personalize para cada vaga aplicada
    4. Solicite feedback de recrutadores da área

    💰 **ATENÇÃO:** Com uma chave API DeepSeek válida, você receberia:
    • Análise personalizada baseada no conteúdo real da vaga
    • Sugestões específicas do setor de {job_title}
    • Reformulação completa do texto do currículo
    • Exemplos concretos de reformulação

    Para ativar a IA completa, adicione sua chave API nas configurações.
    """

    def _generate_stub_optimized_resume(self, resume_data: Dict[str, Any], job_data: Dict[str, Any],
                                        analysis_results: Dict[str, Any]) -> str:
        name = resume_data.get('name', 'SEU NOME COMPLETO')
        email = resume_data.get('email', 'seu.email@profissional.com')
        phone = resume_data.get('phone', '(11) 99999-9999')

        job_title = job_data.get('title', 'Desenvolvedor')
        company = job_data.get('company', 'Empresa do Setor')

        overall_score = analysis_results.get('overall_score', 0)
        experience_years = analysis_results.get('experience_analysis', {}).get('total_experience_years', 3)

        skills_analysis = analysis_results.get('skills_analysis', {})
        exact_matches = skills_analysis.get('exact_matches', [])
        matching_skill_names = [match.get('job_skill', {}).get('name', '') for match in exact_matches[:6]]

        if not matching_skill_names:
            matching_skill_names = ['Python', 'JavaScript', 'SQL', 'Django', 'React', 'Git']

        return f"""
    {name.upper()}
    São Paulo, SP | {phone} | {email} | LinkedIn: linkedin.com/in/seuperfil

    --------------------------------------------------------------------

    RESUMO PROFISSIONAL
    Profissional com {experience_years}+ anos de experiência em {job_title.lower()}. 
    Especializado em {', '.join(matching_skill_names[:3])} com comprovada expertise no desenvolvimento 
    de soluções tecnológicas inovadoras. Busco oportunidade para contribuir com o crescimento da {company}, 
    aplicando minhas habilidades em {matching_skill_names[0] if matching_skill_names else 'tecnologias modernas'} 
    e {matching_skill_names[1] if len(matching_skill_names) > 1 else 'metodologias ágeis'}.

    --------------------------------------------------------------------

    EXPERIÊNCIA PROFISSIONAL

    **{job_title} Senior** | Empresa Anterior | Jan 2020 - Presente
    • Liderança no desenvolvimento de aplicações web utilizando {', '.join(matching_skill_names[:2])}
    • Implementação de APIs RESTful que resultaram em aumento de 40% na performance do sistema
    • Coordenação de equipe de 5 desenvolvedores em ambiente Agile/Scrum
    • Redução de 30% no tempo de deploy através da implementação de pipelines CI/CD

    **Analista de Sistemas** | Empresa Anterior | Mar 2018 - Dez 2019
    • Análise e implementação de sistemas corporativos integrados
    • Automação de processos manuais, reduzindo tempo de operação em 25%
    • Suporte técnico especializado e treinamento de usuários finais

    --------------------------------------------------------------------

    FORMAÇÃO ACADÊMICA

    **Bacharelado em Ciência da Computação**
    Universidade de São Paulo (USP) | Conclusão: 2017

    **Pós-Graduação em Engenharia de Software**
    FIAP | Conclusão: 2019

    --------------------------------------------------------------------

    HABILIDADES TÉCNICAS

    **Linguagens de Programação:** {', '.join(matching_skill_names[:4])}
    **Frameworks & Bibliotecas:** {', '.join(matching_skill_names[4:6] if len(matching_skill_names) > 4 else ['Django', 'React', 'Node.js'])}
    **Banco de Dados:** MySQL, PostgreSQL, MongoDB
    **Ferramentas de DevOps:** Docker, AWS, Jenkins, Git
    **Metodologias:** Agile, Scrum, Kanban, DevOps

    --------------------------------------------------------------------

    IDIOMAS

    • Português: Nativo
    • Inglês: Avançado (Leitura/Escrita), Intermediário (Conversação)
    • Espanhol: Intermediário

    --------------------------------------------------------------------

    CERTIFICAÇÕES

    • AWS Certified Cloud Practitioner
    • Scrum Foundation Professional Certificate
    • Microsoft Certified: Azure Fundamentals

    --------------------------------------------------------------------

    [CURRÍCULO OTIMIZADO AUTOMATICAMENTE - MODO DEMONSTRAÇÃO]
    • Compatibilidade com a vaga: {overall_score}%
    • Layout otimizado para 2 páginas e sistemas ATS
    • Com API válida, o currículo seria personalizado com seus dados reais
    • Estrutura profissional seguindo melhores práticas do mercado
    """
