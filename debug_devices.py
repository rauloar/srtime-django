from rest_framework.test import APIClient
from core.models import Device
from django.contrib.auth import get_user_model
import json

def run():
    # Patch ALLOWED_HOSTS
    from django.conf import settings
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS += ['testserver']

    client = APIClient()
    User = get_user_model()
    admin, _ = User.objects.get_or_create(username='admin_test', defaults={'is_superuser': True, 'is_staff': True})
    client.force_authenticate(user=admin)
    
    count = Device.objects.count()
    print(f"Device Count in DB: {count}")
    
    print("GET /api/v1/devices/")
    response = client.get('/api/v1/devices/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response Data Type: {type(data)}")
        if isinstance(data, list):
            print(f"List Length: {len(data)}")
            print(json.dumps(data, indent=2))
        else:
            print(json.dumps(data, indent=2))
    else:
        print(response.content.decode())

run()
