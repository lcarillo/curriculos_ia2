from django.http import HttpResponseForbidden
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .models import UsageCounter


class SubscriptionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip middleware for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None

        # Skip for anonymous users
        if not request.user.is_authenticated:
            return None

        # Allow access to billing pages
        if request.path.startswith('/billing/') or request.path.startswith('/users/'):
            return None

        # Check if user has active subscription or is within free limits
        try:
            usage_counter = UsageCounter.objects.get(user=request.user)

            # If user is trying to access analysis features without subscription
            if request.path.startswith('/analysis/') and not usage_counter.can_perform_analysis():
                # Redirect to pricing page or show message
                from django.shortcuts import redirect
                return redirect(reverse('pricing'))

            if request.path.startswith('/resumes/export') and not usage_counter.can_export():
                # Redirect to pricing page or show message
                from django.shortcuts import redirect
                return redirect(reverse('pricing'))

        except UsageCounter.DoesNotExist:
            # Create usage counter if it doesn't exist
            UsageCounter.objects.create(user=request.user)

        return None