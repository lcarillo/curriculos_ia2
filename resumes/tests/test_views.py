from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class ResumesViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
    
    def test_upload_resume_view(self):
        response = self.client.get(reverse('upload_resume'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/upload.html')
