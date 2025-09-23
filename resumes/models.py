from django.db import models
from django.contrib.auth.models import User
import json
import logging

logger = logging.getLogger(__name__)


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_file = models.FileField(upload_to='resumes/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    file_type = models.CharField(max_length=10)
    extracted_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.file_name}"

    def get_extracted_data(self) -> dict:
        """Retorna dados extraídos como dicionário seguro"""
        if not self.extracted_data:
            return {}

        try:
            if isinstance(self.extracted_data, str):
                return json.loads(self.extracted_data)
            return self.extracted_data
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Erro ao decodificar dados do currículo {self.id}: {str(e)}")
            return {}

    def get_detected_language(self) -> str:
        """Retorna idioma detectado"""
        return self.get_extracted_data().get('detected_language', 'pt')

    def get_primary_area(self) -> str:
        """Retorna área principal detectada"""
        return self.get_extracted_data().get('area_detected', 'general')

    def get_skills_count(self) -> int:
        """Retorna número de habilidades detectadas"""
        return len(self.get_extracted_data().get('skills', []))

    def get_personal_info(self) -> dict:
        """Retorna informações pessoais"""
        return self.get_extracted_data().get('personal_info', {})