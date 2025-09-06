import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curriculos_ia.settings')
django.setup()

User = get_user_model()

# Versão SEGURA - Falha se não tiver variáveis
try:
    admin_user = os.environ['ADMIN_USERNAME']  # Falha se não existir
    admin_pass = os.environ['ADMIN_PASSWORD']  # Falha se não existir
    admin_email = os.environ['ADMIN_EMAIL']  # Falha se não existir

    if not User.objects.filter(is_superuser=True).exists():
        user = User.objects.create_superuser(
            username=admin_user,
            email=admin_email,
            password=admin_pass
        )
        print(f"✅ Superusuário criado: {admin_user}")

except KeyError as e:
    print(f"❌ Variável de ambiente faltando: {e}")
except Exception as e:
    print(f"❌ Erro: {e}")