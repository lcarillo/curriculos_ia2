from django.db import models
from django.contrib.auth.models import User


class Plan(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    periodicity = models.CharField(max_length=20, choices=[
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('lifetime', 'Vitalício'),
    ])
    price_cents = models.IntegerField()
    stripe_price_id = models.CharField(max_length=100)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['price_cents']
    
    def __str__(self):
        return self.name
    
    @property
    def price(self):
        return self.price_cents / 100


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Ativa'),
        ('canceled', 'Cancelada'),
        ('past_due', 'Atrasada'),
        ('incomplete', 'Incompleta'),
    ])
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=100)
    stripe_subscription_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
    @property
    def is_active(self):
        return self.status == 'active'


class UsageCounter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    analyses_count = models.IntegerField(default=0)
    exports_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Usage for {self.user.username}"
    
    def can_perform_analysis(self):
        """Verifica se usuário pode realizar análise (limite free: 2)"""
        from django.conf import settings
        if hasattr(self.user, 'subscription') and self.user.subscription.is_active:
            return True
        return self.analyses_count < 2
    
    def can_export(self):
        """Verifica se usuário pode exportar (limite free: 2)"""
        from django.conf import settings
        if hasattr(self.user, 'subscription') and self.user.subscription.is_active:
            return True
        return self.exports_count < 2
