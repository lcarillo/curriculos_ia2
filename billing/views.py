from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import stripe
import json
from datetime import datetime
from .models import Plan, Subscription, UsageCounter
from .services.stripe_client import create_checkout_session, create_billing_portal_session


@login_required
def checkout(request, plan_slug):
    """View para criar sessão de checkout do Stripe"""
    try:
        print(f"=== INICIANDO CHECKOUT ===")
        print(f"Plano solicitado: {plan_slug}")
        print(f"Usuário: {request.user}")

        plan = Plan.objects.get(slug=plan_slug, is_active=True)
        print(f"Plano encontrado: {plan.name}")
        print(f"Stripe Price ID: {plan.stripe_price_id}")

        # URLs dinâmicas baseadas no domínio atual
        success_url = request.build_absolute_uri(reverse('checkout_success'))
        cancel_url = request.build_absolute_uri(reverse('checkout_cancel'))

        # Criar sessão de checkout
        session = create_checkout_session(
            request.user,
            plan,
            success_url,
            cancel_url
        )

        print(f"URL do Checkout: {session.url}")
        return redirect(session.url)

    except Plan.DoesNotExist:
        print("❌ ERRO: Plano não encontrado")
        messages.error(request, 'Plano não encontrado.')
        return redirect('pricing')
    except Exception as e:
        print(f"❌ ERRO GERAL: {str(e)}")
        import traceback
        traceback.print_exc()  # Mostra o traceback completo
        messages.error(request, f'Erro ao processar pagamento: {str(e)}')
        return redirect('pricing')


@login_required
def success(request):
    """View para sucesso no checkout"""
    # Verifica se a assinatura foi criada via webhook
    if hasattr(request.user, 'subscription') and request.user.subscription.is_active:
        messages.success(request, 'Assinatura ativada com sucesso! 🎉')
    else:
        messages.info(request, 'Pagamento processado! Sua assinatura será ativada em instantes.')

    return redirect('dashboard')


@login_required
def cancel(request):
    """View para cancelamento no checkout"""
    messages.warning(request, 'Pagamento cancelado.')
    return redirect('pricing')


@login_required
def billing_portal(request):
    """View para portal de billing do Stripe"""
    try:
        if hasattr(request.user, 'subscription') and request.user.subscription.stripe_customer_id:
            # URL dinâmica baseada no domínio atual
            return_url = request.build_absolute_uri(reverse('dashboard'))

            session = create_billing_portal_session(
                request.user.subscription.stripe_customer_id,
                return_url
            )
            return redirect(session.url)
        else:
            messages.error(request, 'Nenhuma assinatura encontrada.')
            return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'Erro ao acessar portal de billing: {str(e)}')
        return redirect('dashboard')


@csrf_exempt
def stripe_webhook(request):
    """View para processar webhooks do Stripe"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Processar eventos relevantes
    event_type = event['type']
    data_object = event['data']['object']

    print(f"📨 Recebido evento do Stripe: {event_type}")

    # Eventos de checkout
    if event_type == 'checkout.session.completed':
        handle_checkout_session(data_object)

    # Eventos de assinatura (CRÍTICOS para sincronização)
    elif event_type == 'customer.subscription.updated':
        handle_subscription_event(data_object, 'updated')
    elif event_type == 'customer.subscription.deleted':
        handle_subscription_event(data_object, 'deleted')
    elif event_type == 'customer.subscription.created':
        handle_subscription_event(data_object, 'created')

    # Eventos de invoice
    elif event_type == 'invoice.paid':
        handle_invoice_event(data_object, 'paid')
    elif event_type == 'invoice.payment_failed':
        handle_invoice_event(data_object, 'payment_failed')

    return HttpResponse(status=200)


def handle_checkout_session(session):
    """Processar sessão de checkout concluída"""
    from .models import Subscription, Plan
    from django.contrib.auth.models import User

    user_id = session.metadata.get('user_id')
    plan_id = session.metadata.get('plan_id')

    try:
        user = User.objects.get(id=user_id)
        plan = Plan.objects.get(id=plan_id)

        # Obter detalhes da assinatura do Stripe
        stripe_subscription = stripe.Subscription.retrieve(session.subscription)

        # Criar ou atualizar assinatura
        Subscription.objects.update_or_create(
            user=user,
            defaults={
                'plan': plan,
                'status': stripe_subscription.status,
                'stripe_customer_id': session.customer,
                'stripe_subscription_id': session.subscription,
                'current_period_start': datetime.fromtimestamp(stripe_subscription.current_period_start),
                'current_period_end': datetime.fromtimestamp(stripe_subscription.current_period_end)
            }
        )

        print(f"✅ Assinatura criada/atualizada para o usuário {user.username}")

    except (User.DoesNotExist, Plan.DoesNotExist) as e:
        print(f"❌ Erro ao processar checkout: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao processar checkout: {e}")


def handle_subscription_event(subscription, event_type):
    """Processar eventos de assinatura"""
    from .models import Subscription
    from django.contrib.auth.models import User

    try:
        stripe_subscription_id = subscription['id']
        customer_id = subscription['customer']
        status = subscription['status']

        print(f"🔔 Evento de assinatura: {event_type}, Status: {status}, ID: {stripe_subscription_id}")

        # Encontrar a assinatura no banco de dados
        try:
            sub = Subscription.objects.get(stripe_subscription_id=stripe_subscription_id)
        except Subscription.DoesNotExist:
            # Se não encontrar, tentar encontrar pelo customer_id
            try:
                user = User.objects.get(subscription__stripe_customer_id=customer_id)
                sub = user.subscription
            except (User.DoesNotExist, Subscription.DoesNotExist):
                print(f"❌ Assinatura não encontrada para ID: {stripe_subscription_id}")
                return

        # Atualizar status
        sub.status = status

        # Extrair datas de período - verificar em items.data[0] se não estiver no nível raiz
        current_period_start = None
        current_period_end = None

        # Primeiro tenta obter do nível raiz
        if subscription.get('current_period_start'):
            current_period_start = datetime.fromtimestamp(subscription['current_period_start'])
        elif (subscription.get('items') and
              subscription['items'].get('data') and
              len(subscription['items']['data']) > 0 and
              subscription['items']['data'][0].get('current_period_start')):
            current_period_start = datetime.fromtimestamp(subscription['items']['data'][0]['current_period_start'])

        # Mesma lógica para current_period_end
        if subscription.get('current_period_end'):
            current_period_end = datetime.fromtimestamp(subscription['current_period_end'])
        elif (subscription.get('items') and
              subscription['items'].get('data') and
              len(subscription['items']['data']) > 0 and
              subscription['items']['data'][0].get('current_period_end')):
            current_period_end = datetime.fromtimestamp(subscription['items']['data'][0]['current_period_end'])

        # Atualizar datas se encontradas
        if current_period_start:
            sub.current_period_start = current_period_start
        if current_period_end:
            sub.current_period_end = current_period_end

        # Atualizar outras datas se disponíveis
        if subscription.get('canceled_at'):
            sub.canceled_at = datetime.fromtimestamp(subscription['canceled_at'])
        if subscription.get('ended_at'):
            sub.ended_at = datetime.fromtimestamp(subscription['ended_at'])

        sub.save()
        print(f"✅ Assinatura {stripe_subscription_id} atualizada para status {status}")
        print(f"📅 Novo período: {sub.current_period_start} até {sub.current_period_end}")

    except Exception as e:
        print(f"❌ Erro ao processar evento de assinatura: {e}")
        import traceback
        traceback.print_exc()

def handle_invoice_event(invoice, event_type):
    """Processar eventos de fatura"""
    print(f"🧾 Evento de fatura: {event_type}, ID: {invoice.get('id')}")
    # Você pode adicionar lógica adicional para processar faturas aqui