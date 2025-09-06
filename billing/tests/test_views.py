from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class BillingViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
    
    def test_success_view(self):
        response = self.client.get(reverse('checkout_success'))
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
    
    def test_cancel_view(self):
        response = self.client.get(reverse('checkout_cancel'))
        self.assertEqual(response.status_code, 302)  # Redirect to pricing
