import os
import json
import httpx
from typing import Dict, Any, Optional


class DeepSeekClient:
    def __init__(self):
        self.api_key = os.environ.get('DEEPSEEK_API_KEY')
        self.base_url = os.environ.get('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
        self.model = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')
        self.use_stub = not self.api_key
    
    def generate_suggestions(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Gera sugestões de melhoria para o currículo baseado na vaga"""
        if self.use_stub:
            return self._generate_stub_suggestions(resume_data, job_data)
        
        prompt = self._build_suggestions_prompt(resume_data, job_data)
        return self._make_api_call(prompt)
    
    def optimize_resume(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Gera um currículo otimizado para a vaga específica"""
        if self.use_stub:
            return self._generate_stub_optimized_resume(resume_data, job_data)
        
        prompt = self._build_optimize_prompt(resume_data, job_data)
        return self._make_api_call(prompt)
    
    def _make_api_call(self, prompt: str) -> str:
        """Faz chamada para a API do DeepSeek"""
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
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                return result['choices'][0]['message']['content']
                
        except Exception as e:
            # Fallback para stub em caso de erro
            return f"Erro na API DeepSeek: {str(e)}. Usando sugestões simuladas."
    
    def _build_suggestions_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Constrói o prompt para geração de sugestões"""
        resume_json = json.dumps(resume_data, ensure_ascii=False, indent=2)
        job_json = json.dumps(job_data, ensure_ascii=False, indent=2)
        
        return f"""
        Como especialista em recrutamento e otimização de currículos, analise o currículo abaixo em relação à vaga de emprego e forneça sugestões específicas de melhoria.

        DADOS DO CURRÍCULO:
        {resume_json}

        DESCRIÇÃO DA VAGA:
        {job_json}

        Forneça sugestões concretas para:
        1. Ajustar as palavras-chave do currículo para corresponder melhor à vaga
        2. Melhorar a descrição das experiências profissionais
        3. Destacar habilidades relevantes para a vaga
        4. Sugerir reformulações para aumentar o impacto
        5. Identificar lacunas e sugerir como abordá-las

        Formate a resposta em tópicos claros e objetivos.
        """
    
    def _build_optimize_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Constrói o prompt para otimização do currículo"""
        resume_json = json.dumps(resume_data, ensure_ascii=False, indent=2)
        job_json = json.dumps(job_data, ensure_ascii=False, indent=2)
        
        return f"""
        Como especialista em recrutamento, otimize este currículo para se adequar perfeitamente à vaga específica. Mantenha todas informações verdadeiras, mas reformule para destacar as qualificações mais relevantes.

        DADOS DO CURRÍCULO ORIGINAL:
        {resume_json}

        DESCRIÇÃO DA VAGA:
        {job_json}

        Gere um currículo otimizado completo no seguinte formato:

        NOME COMPLETO
        Email: | Telefone: | LinkedIn: (se disponível)

        RESUMO PROFISSIONAL
        [Escreva um resumo compelling que destaque como as experiências e habilidades se alinham com a vaga]

        EXPERIÊNCIA PROFISSIONAL
        [Reformule as experiências para destacar conquistas e habilidades relevantes para a vaga. Use números e métricas quando possível]

        FORMAÇÃO ACADÊMICA
        [Mantenha a formação, mas pode reordenar se relevante]

        HABILIDADES TÉCNICAS
        [Destaque as habilidades mais relevantes para a vaga, agrupando por categoria]

        IDIOMAS
        [Mantenha os idiomas]

        Certifique-se de que o currículo seja claro, conciso e direcionado para a vaga específica.
        """
    
    def _generate_stub_suggestions(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Gera sugestões simuladas quando a API não está disponível"""
        return """
        SUGESTÕES DE OTIMIZAÇÃO (Modo de Demonstração):

        1. PALAVRAS-CHAVE: 
        - Adicione palavras-chave da descrição da vaga como "Python", "Django", "APIs REST"
        - Use termos específicos mencionados na vaga

        2. EXPERIÊNCIAS PROFISSIONAIS:
        - Reformule para focar em resultados e conquistas
        - Use números para quantificar impactos (ex: "aumentou eficiência em 30%")
        - Destaque experiências mais relevantes para a vaga

        3. HABILIDADES:
        - Reorganize a seção de habilidades para destacar as mais relevantes
        - Agrupe habilidades técnicas por categoria
        - Adicione habilidades solicitadas na vaga que você possui

        4. FORMATAÇÃO:
        - Mantenha o currículo em 1 página
        - Use espaçamento consistente e fontes profissionais
        - Destaque seções importantes

        Estas são sugestões gerais. Com uma chave API válida, receberia recomendações específicas baseadas na vaga.
        """
    
    def _generate_stub_optimized_resume(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Gera um currículo otimizado simulado quando a API não está disponível"""
        name = resume_data.get('name', 'Seu Nome')
        email = resume_data.get('email', 'seu.email@exemplo.com')
        phone = resume_data.get('phone', '(11) 99999-9999')
        
        return f"""
        {name.upper()}
        Email: {email} | Telefone: {phone} | LinkedIn: linkedin.com/in/seuperfil

        RESUMO PROFISSIONAL
        Profissional com experiência nas áreas mencionadas na vaga. Busco oportunidade para aplicar minhas habilidades e contribuir para o sucesso da empresa.

        EXPERIÊNCIA PROFISSIONAL
        • Reformule suas experiências para destacar conquistas mensuráveis
        • Use verbos de ação como "desenvolvi", "implementei", "otimizei"
        • Inclua números para quantificar resultados quando possível

        FORMAÇÃO ACADÊMICA
        • Mantenha suas informações educacionais verdadeiras

        HABILIDADES TÉCNICAS
        • Linguagens: Python, JavaScript, etc.
        • Frameworks: Django, React, etc.
        • Ferramentas: Git, Docker, AWS
        • Adicione habilidades específicas mencionadas na vaga

        IDIOMAS
        • Português: Nativo
        • Inglês: Intermediário/Avançado (ajuste conforme sua realidade)

        Este é um exemplo de currículo otimizado. Com uma chave API válida, receberia um currículo personalizado baseado na vaga específica.
        """
