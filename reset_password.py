import os
import django
import sys
sys.path.append('c:\\Proyectos\\srtime-django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRTimeWeb.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    u = User.objects.get(username='raul')
    u.set_password('admin')
    u.save()
    print("Password for raul set to admin")
except Exception as e:
    print(e)
