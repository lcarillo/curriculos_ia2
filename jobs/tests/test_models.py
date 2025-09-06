from django.test import TestCase
from django.contrib.auth.models import User
from jobs.models import JobPosting


class JobPostingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
    
    def test_create_job_posting(self):
        job = JobPosting.objects.create(
            user=self.user,
            title='Desenvolvedor Python',
            company='Tech Company',
            description='Vaga para desenvolvedor Python com Django'
        )
        self.assertEqual(str(job), 'Desenvolvedor Python - Tech Company')
