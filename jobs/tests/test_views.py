from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class JobsViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
    
    def test_create_job_view(self):
        response = self.client.get(reverse('create_job'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/new.html')
