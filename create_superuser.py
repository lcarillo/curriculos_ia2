# create_admin.py (versão segura)
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curriculos_ia.settings')
django.setup()

User = get_user_model()

# Usa variáveis de ambiente ou valores padrão
admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@seusite.com')

if not User.objects.filter(is_superuser=True).exists():
    try:
        user = User.objects.create_superuser(
            username=admin_user,
            email=admin_email,
            password=admin_pass
        )
        print(f"✅ Superusuário criado: {admin_user} / {admin_pass}")
    except Exception as e:
        print(f"❌ Erro: {e}")