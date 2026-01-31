"""
Script para resetear la contraseña del usuario raul
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRTimeWeb.settings')
django.setup()

from django.contrib.auth.models import User

# Obtener usuario
user = User.objects.get(username='raul')

# Establecer nueva contraseña
new_password = 'admin123'
user.set_password(new_password)
user.save()

print(f"✅ Contraseña actualizada para el usuario '{user.username}'")
print(f"   Nueva contraseña: {new_password}")
print(f"   Superuser: {user.is_superuser}")
print(f"   Staff: {user.is_staff}")
