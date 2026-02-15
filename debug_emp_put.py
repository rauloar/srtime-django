import requests
import json
import os
import django
from django.conf import settings

# Setup Django to use its models/settings if needed (though we use requests here)
import sys
sys.path.append('c:\\Proyectos\\srtime-django')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import User as DeviceUser

# Use APIClient to avoid authentication issues if possible, or simulate admin
client = APIClient()
# Create or get superuser
admin, created = User.objects.get_or_create(username='admin_test', defaults={'email': 'admin@test.com'})
client.force_authenticate(user=admin)

# Get employees
print("GET /api/v1/employees/")
response = client.get('/api/v1/employees/')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if isinstance(data, list) and len(data) > 0:
        print("First item keys:", data[0].keys())
        print("First item content:", json.dumps(data[0], indent=2))
        
        # Try to update it
        emp_id = data[0]['id']
        print(f"\nPUT /api/v1/employees/{emp_id}/")
        
        # Payload simulation (what frontend sends)
        # Frontend sends everything in 'data[0]' plus modified fields
        payload = data[0].copy()
        payload['name'] = "Updated Name Test"
        
        # Check if uid/device are present
        if 'uid' not in payload:
            print("CRITICAL: 'uid' missing in GET response!")
        if 'device' not in payload:
            print("CRITICAL: 'device' missing in GET response!")
            
        # Try PUT
        resp_put = client.put(f'/api/v1/employees/{emp_id}/', payload, format='json')
        print(f"PUT Status: {resp_put.status_code}")
        if resp_put.status_code != 200:
            print("PUT Error:", resp_put.content.decode())
    else:
        print("No employees found.")
else:
    print("Error getting employees:", response.content)
