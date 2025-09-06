import stripe
import os
from django.conf import settings
from django.contrib.auth.models import User


def get_stripe_client():
    """Retorna cliente Stripe configurado"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def create_checkout_session(user: User, plan, success_url: str, cancel_url: str):
    """Cria sessão de checkout do Stripe"""
    print(f"=== CRIANDO SESSÃO CHECKOUT ===")
    print(f"Usuário: {user.email}")
    print(f"Plano: {plan.name} (ID: {plan.stripe_price_id})")
    print(f"Success URL: {success_url}")
    print(f"Cancel URL: {cancel_url}")

    stripe = get_stripe_client()

    # Verifica se usuário já é cliente Stripe
    customer_id = None
    if hasattr(user, 'subscription'):
        customer_id = user.subscription.stripe_customer_id

    print(f"Customer ID: {customer_id}")

    # Cria sessão de checkout
    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            customer_email=user.email if not customer_id else None,
            payment_method_types=['card'],
            line_items=[{
                'price': plan.stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': user.id,
                'plan_id': plan.id
            }
        )

        print(f"✅ Sessão criada com ID: {session.id}")
        return session

    except Exception as e:
        print(f"❌ ERRO ao criar sessão Stripe: {str(e)}")
        raise e


def create_billing_portal_session(customer_id: str, return_url: str):
    """Cria sessão para portal de billing do Stripe"""
    stripe = get_stripe_client()

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url
    )

    return session


def handle_webhook_event(payload, sig_header):
    """Processa eventos webhook do Stripe"""
    stripe = get_stripe_client()
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        raise ValueError("Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise ValueError("Invalid signature")

    # Processa eventos relevantes
    if event['type'] == 'checkout.session.completed':
        handle_checkout_completed(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    elif event['type'] == 'invoice.paid':
        handle_invoice_paid(event['data']['object'])

    return event


def handle_checkout_completed(session):
    """Handle checkout.session.completed event"""
    from .models import Subscription, Plan
    from django.contrib.auth.models import User

    user_id = session.metadata.get('user_id')
    plan_id = session.metadata.get('plan_id')

    try:
        user = User.objects.get(id=user_id)
        plan = Plan.objects.get(id=plan_id)

        # Get subscription details
        stripe = get_stripe_client()
        subscription = stripe.Subscription.retrieve(session.subscription)

        # Create or update subscription
        Subscription.objects.update_or_create(
            user=user,
            defaults={
                'plan': plan,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'stripe_customer_id': session.customer,
                'stripe_subscription_id': session.subscription,
            }
        )

    except (User.DoesNotExist, Plan.DoesNotExist) as e:
        print(f"Error handling checkout completed: {e}")


def handle_subscription_updated(subscription):
    """Handle customer.subscription.updated event"""
    from .models import Subscription

    try:
        db_subscription = Subscription.objects.get(
            stripe_subscription_id=subscription.id
        )
        db_subscription.status = subscription.status
        db_subscription.current_period_start = subscription.current_period_start
        db_subscription.current_period_end = subscription.current_period_end
        db_subscription.save()

    except Subscription.DoesNotExist:
        print(f"Subscription not found: {subscription.id}")


def handle_subscription_deleted(subscription):
    """Handle customer.subscription.deleted event"""
    from .models import Subscription

    try:
        db_subscription = Subscription.objects.get(
            stripe_subscription_id=subscription.id
        )
        db_subscription.status = 'canceled'
        db_subscription.save()

    except Subscription.DoesNotExist:
        print(f"Subscription not found: {subscription.id}")


def handle_invoice_paid(invoice):
    """Handle invoice.paid event"""
    # Você pode implementar lógica adicional aqui
    # como enviar emails de confirmação, etc.
    pass