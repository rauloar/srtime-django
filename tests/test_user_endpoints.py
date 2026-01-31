import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_user_crud():
    client = APIClient()
    # Create superuser for authentication
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
    client.force_authenticate(user=admin)

    # Create user
    resp = client.post(reverse('auth_users_list'), {
        'username': 'testuser',
        'password': 'testpass',
        'email': 'testuser@example.com',
        'is_active': True
    })
    assert resp.status_code == 201
    user_id = resp.data['id']

    # List users
    resp = client.get(reverse('auth_users_list'))
    assert resp.status_code == 200
    assert any(u['username'] == 'testuser' for u in resp.data)

    # Update password
    resp = client.put(reverse('auth_user_password_update', args=[user_id]), {'password': 'newpass'})
    assert resp.status_code == 200

    # Delete user
    resp = client.delete(reverse('auth_user_delete', args=[user_id]))
    assert resp.status_code == 204

    # Confirm deletion
    resp = client.get(reverse('auth_users_list'))
    assert not any(u['id'] == user_id for u in resp.data)
