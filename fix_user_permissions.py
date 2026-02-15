"""Add view_user permission to groups that need to see personnel/employees"""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import User

#  Get User content type and view permission
ct = ContentType.objects.get_for_model(User)
view_perm = Permission.objects.get(content_type=ct, codename='view_user')

# Groups that should see users from devices
groups_needing_view = ['hr_manager', 'device_admin', 'viewer']

for group_name in groups_needing_view:
    try:
        group = Group.objects.get(name=group_name)
        if view_perm not in group.permissions.all():
            group.permissions.add(view_perm)
            print(f'✓ Added view_user to {group_name}')
        else:
            print(f'- {group_name} already has view_user')
    except Group.DoesNotExist:
        print(f'✗ Group {group_name} does not exist')

print('\n=== Updated Group Permissions ===')
for g in Group.objects.all():
    user_perms = [p.codename for p in g.permissions.filter(content_type=ct)]
    print(f'{g.name}: {user_perms}')
