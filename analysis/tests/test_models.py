from django.test import TestCase
from django.contrib.auth.models import User
from resumes.models import Resume
from jobs.models import JobPosting
from analysis.models import Analysis


class AnalysisModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.resume = Resume.objects.create(
            user=self.user,
            file_name='test.pdf',
            file_size=1024,
            file_type='.pdf',
            status='completed'
        )
        self.job = JobPosting.objects.create(
            user=self.user,
            title='Test Job',
            description='Test Description'
        )
    
    def test_create_analysis(self):
        analysis = Analysis.objects.create(
            user=self.user,
            resume=self.resume,
            job=self.job,
            score=0.85
        )
        self.assertEqual(str(analysis), f'Analysis: {self.resume.file_name} ↔ {self.job.title}')
