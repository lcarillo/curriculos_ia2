from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Profile


class ProfileModelTest(TestCase):
    def test_profile_creation(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.user, user)
