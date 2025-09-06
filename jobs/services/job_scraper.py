import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any


def scrape_job_posting(url: str) -> Dict[str, Any]:
    """
    Extrai informações de uma vaga a partir de uma URL
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts e styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Tenta encontrar o título
        title = extract_title(soup)
        
        # Tenta encontrar a empresa
        company = extract_company(soup)
        
        # Extrai o texto principal
        text = soup.get_text(separator='\n', strip=True)
        
        # Limpa o texto (remove excesso de espaços e quebras)
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        
        return {
            'title': title,
            'company': company,
            'description': text[:5000],  # Limita o tamanho
            'url': url,
            'raw_html': str(soup)[:10000]  # Limita o tamanho para armazenamento
        }
        
    except Exception as e:
        raise Exception(f"Erro ao extrair dados da URL: {str(e)}")


def extract_title(soup):
    """Extrai título da vaga"""
    # Tenta encontrar por meta tags
    meta_title = soup.find('meta', property='og:title')
    if meta_title and meta_title.get('content'):
        return meta_title['content']
    
    # Tenta encontrar por tag title
    if soup.title:
        return soup.title.string
    
    # Tenta encontrar por headings
    for tag in ['h1', 'h2', 'h3']:
        heading = soup.find(tag)
        if heading and heading.text.strip():
            return heading.text.strip()
    
    return "Título não identificado"


def extract_company(soup):
    """Extrai nome da empresa"""
    # Tenta encontrar por meta tags
    meta_company = soup.find('meta', property='og:site_name')
    if meta_company and meta_company.get('content'):
        return meta_company['content']
    
    # Procura por padrões comuns no texto
    text = soup.get_text().lower()
    company_patterns = [
        r'empresa:\s*([^\n]+)',
        r'company:\s*([^\n]+)',
        r'contratante:\s*([^\n]+)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:LTDA|S\.A|SA|LTD)'
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "Empresa não identificada"
