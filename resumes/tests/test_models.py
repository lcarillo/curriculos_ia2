from django.test import TestCase
from django.contrib.auth.models import User
from resumes.models import Resume


class ResumeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
    
    def test_create_resume(self):
        resume = Resume.objects.create(
            user=self.user,
            file_name='test.pdf',
            file_size=1024,
            file_type='.pdf',
            status='pending'
        )
        self.assertEqual(str(resume), f"{self.user.username} - test.pdf")
