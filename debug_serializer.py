from core.models import User
from core.serializers import UserSerializer
import json

u = User.objects.first()
if u:
    s = UserSerializer(u)
    print(json.dumps(s.data, indent=2))
else:
    print("No users found")
