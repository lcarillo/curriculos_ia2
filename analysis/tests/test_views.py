from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AnalysisViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
    
    def test_create_analysis_view(self):
        response = self.client.get(reverse('create_analysis'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis/create.html')
