import hashlib
import json
import redis
from typing import Dict, Any, Optional, List
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class AnalysisCacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=getattr(settings, 'REDIS_HOST', 'localhost'),
            port=getattr(settings, 'REDIS_PORT', 6379),
            db=getattr(settings, 'REDIS_DB', 0),
            decode_responses=True
        )
        self.cache_timeout = 86400

    def _generate_cache_key(self, content_type: str, *args) -> str:
        content = f"{content_type}:{':'.join(str(arg) for arg in args)}"
        return f"analysis:{hashlib.md5(content.encode()).hexdigest()}"

    def get_cached_analysis(self, resume_text: str, job_description: str) -> Optional[Dict[str, Any]]:
        try:
            key = self._generate_cache_key("compatibility", resume_text, job_description)
            cached_result = self.redis_client.get(key)
            if cached_result:
                logger.info("Cache HIT para análise de compatibilidade")
                return json.loads(cached_result)
            return None
        except Exception as e:
            logger.error(f"Erro ao acessar cache: {str(e)}")
            return None

    def set_cached_analysis(self, resume_text: str, job_description: str, result: Dict[str, Any]) -> None:
        try:
            key = self._generate_cache_key("compatibility", resume_text, job_description)
            self.redis_client.setex(key, self.cache_timeout, json.dumps(result))
        except Exception as e:
            logger.error(f"Erro ao armazenar no cache: {str(e)}")

    def get_cached_suggestions(self, prompt: str) -> Optional[str]:
        try:
            key = self._generate_cache_key("suggestions", prompt)
            return self.redis_client.get(key)
        except Exception as e:
            return None

    def set_cached_suggestions(self, prompt: str, result: str) -> None:
        try:
            key = self._generate_cache_key("suggestions", prompt)
            self.redis_client.setex(key, self.cache_timeout, result)
        except Exception as e:
            logger.error(f"Erro ao armazenar sugestões: {str(e)}")

    def increment_user_analysis_count(self, user_id: int) -> int:
        try:
            key = f"user_analysis_count:{user_id}"
            return self.redis_client.incr(key)
        except:
            return 0

    def get_global_skills_frequency(self) -> Dict[str, int]:
        try:
            key = "global_skills_frequency"
            data = self.redis_client.get(key)
            return json.loads(data) if data else {}
        except:
            return {}

    def update_global_skills_frequency(self, skills: List[str]) -> None:
        try:
            key = "global_skills_frequency"
            current = self.get_global_skills_frequency()
            for skill in skills:
                current[skill] = current.get(skill, 0) + 1
            self.redis_client.setex(key, 86400 * 7, json.dumps(current))
        except Exception as e:
            logger.error(f"Erro ao atualizar frequência de habilidades: {str(e)}")
