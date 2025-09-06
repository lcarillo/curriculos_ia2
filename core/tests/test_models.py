from django.test import TestCase
from core.models import SiteSettings


class SiteSettingsModelTest(TestCase):
    def test_create_site_settings(self):
        settings = SiteSettings.objects.create(
            site_name='Test Site',
            site_description='Test Description',
            maintenance_mode=False
        )
        self.assertEqual(str(settings), 'Test Site')
