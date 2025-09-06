from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import stripe
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

        # Criar sessão de checkout - CORRIGIDO
        session = create_checkout_session(
            request.user,
            plan,
            f"http://127.0.0.1:8000/billing/success/",  # URL absoluta
            f"http://127.0.0.1:8000/billing/cancel/"  # URL absoluta
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
    messages.success(request, 'Assinatura ativada com sucesso! 🎉')
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
            session = create_billing_portal_session(
                request.user.subscription.stripe_customer_id,
                f"http://127.0.0.1:8000/dashboard/"  # URL absoluta
            )
            return redirect(session.url)
        else:
            messages.error(request, 'Nenhuma assinatura encontrada.')
            return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'Erro ao acessar portal de billing: {str(e)}')
        return redirect('dashboard')