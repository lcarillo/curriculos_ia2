# create_superuser.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curriculos_ia.settings')
django.setup()

from django.contrib.auth.models import User

# Cria superusuário se não existir
if not User.objects.filter(is_superuser=True).exists():
    user = User.objects.create_superuser(
        username='admin',
        email='lcarillo97@gmail.com',
        password='@Ahmedcorno2'
    )
    print(f"✅ Superusuário criado: {user.username}")
else:
    print("✅ Superusuário já existe")