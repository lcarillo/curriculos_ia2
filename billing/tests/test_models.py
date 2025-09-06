from django.test import TestCase
from django.contrib.auth.models import User
from billing.models import Plan, UsageCounter


class BillingModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.plan = Plan.objects.create(
            name='Test Plan',
            slug='test-plan',
            periodicity='monthly',
            price_cents=1900,
            stripe_price_id='price_test'
        )
    
    def test_create_usage_counter(self):
        usage = UsageCounter.objects.create(user=self.user, analyses_count=1, exports_count=0)
        self.assertEqual(str(usage), f"Usage for {self.user.username}")
    
    def test_usage_counter_limits(self):
        usage = UsageCounter.objects.create(user=self.user, analyses_count=1, exports_count=1)
        
        # Free user should be able to perform 1 more analysis and 1 more export
        self.assertTrue(usage.can_perform_analysis())
        self.assertTrue(usage.can_export())
        
        # Update to exceed limits
        usage.analyses_count = 2
        usage.exports_count = 2
        usage.save()
        
        # Free user should not be able to perform more analyses or exports
        self.assertFalse(usage.can_perform_analysis())
        self.assertFalse(usage.can_export())
