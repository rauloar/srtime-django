from rest_framework.test import APIClient
from core.models import User
from django.contrib.auth import get_user_model
import json

def run():
    # Patch ALLOWED_HOSTS
    from django.conf import settings
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS += ['testserver']

    client = APIClient()
    # Ensure admin user exists for auth
    User = get_user_model() # This is auth.User, not core.User
    admin, created = User.objects.get_or_create(username='admin_test', defaults={'is_superuser': True, 'is_staff': True})
    client.force_authenticate(user=admin)
    
    print("GET /api/v1/employees/")
    response = client.get('/api/v1/employees/')
    if response.status_code != 200:
        print(f"Failed GET: {response.status_code}")
        return

    data = response.json()
    if not isinstance(data, list) or len(data) == 0:
        print("No employees found.")
        return

    target = data[0]
    tid = target['id']
    print(f"Targeting User ID {tid}")
    
    # Prepare payload
    payload = target.copy()
    payload['name'] = "Debug Internal Update"
    
    # Ensure device/uid are present (they should be in target, but verify)
    if 'device' not in payload:
        print("Adding missing device=1")
        payload['device'] = 1
    if 'uid' not in payload:
        print("Adding missing uid=1")
        payload['uid'] = 1
        
    print("Sending Payload:", json.dumps(payload, indent=2))
    
    response = client.put(f'/api/v1/employees/{tid}/', payload, format='json')
    print(f"PUT Status: {response.status_code}")
    print(f"PUT Body: {response.content.decode()}")

run()
