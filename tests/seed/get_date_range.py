import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from core.models import AttendanceLog
from datetime import timedelta

# Encontrar la fecha más reciente
latest = AttendanceLog.objects.order_by('-timestamp').first()
if latest:
    end_date = latest.timestamp.date()
    start_date = end_date - timedelta(days=30)
    print(f'START_DATE={start_date}')
    print(f'END_DATE={end_date}')
    
    # Contar logs en el rango
    count = AttendanceLog.objects.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date).count()
    print(f'LOGS_IN_RANGE={count}')
else:
    print('NO LOGS FOUND')
