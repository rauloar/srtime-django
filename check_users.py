import os
import django
import sys

# Add project root to path
sys.path.append('c:\\Proyectos\\srtime-django')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRTimeWeb.settings') 
# Note: Checking structure, often settings are in 'srtime_project' or 'core'. 
# Based on file structure from previous turns, 'core' has models but settings usually in project folder. 
# Listing dir to find settings.py location is safer first, but assuming 'srtime.settings' or 'core.settings' might fail.
# Let's try to detect settings module or just assume standard 'srtime.settings' if project name is srtime.
# Wait, previous logs showed `c:\Proyectos\srtime-django`.
# Let's look for manage.py to see default settings.

try:
    django.setup()
    from django.contrib.auth import get_user_model
    User = get_user_model()
    print("Users:", [u.username for u in User.objects.all()])
except Exception as e:
    print("Error:", e)
