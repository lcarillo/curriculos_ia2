from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='Currículos IA')
    site_description = models.TextField(default='Analise e otimize seu currículo com IA')
    maintenance_mode = models.BooleanField(default=False)

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

# REMOVA completamente estes modelos se existirem:
# class Resume(models.Model): ...
# class JobPosting(models.Model): ...
# class Analysis(models.Model): ...