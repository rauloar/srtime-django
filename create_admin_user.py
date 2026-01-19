#!/usr/bin/env python
"""Script para crear usuario admin en AuthUser"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRTimeWeb.settings')
django.setup()

from core.models import AuthUser
from django.contrib.auth.hashers import make_password

# Crear usuario admin en AuthUser
try:
    user = AuthUser.objects.get(username='admin')
    print(f'Usuario admin ya existe: {user.username} (role: {user.role})')
except AuthUser.DoesNotExist:
    user = AuthUser.objects.create(
        username='admin',
        password_hash=make_password('admin123'),
        role='admin',
        employee=None,
        active=True
    )
    print(f'Usuario admin creado exitosamente: {user.username} (role: {user.role})')
