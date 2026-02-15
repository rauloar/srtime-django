from django.contrib.auth.models import User

users = User.objects.all()
print(f'Total usuarios: {users.count()}\n')
print('=== USUARIOS DEL SISTEMA ===\n')

for u in users:
    grupos = [g.name for g in u.groups.all()]
    print(f'Username: {u.username}')
    print(f'  Email: {u.email}')
    print(f'  Is Staff: {u.is_staff}')
    print(f'  Is Superuser: {u.is_superuser}')
    print(f'  Is Active: {u.is_active}')
    print(f'  Grupos: {grupos}')
    print()
