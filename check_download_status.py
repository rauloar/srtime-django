"""Check download users job status and verify data persistence"""
from core.models import Job, User, JobLog

# Check last job
jobs = Job.objects.filter(type='download_users').order_by('-created_at')
if jobs.exists():
    j = jobs.first()
    print("=== ÚLTIMO JOB ===")
    print(f"ID: {j.id}")
    print(f"Status: {j.status}")
    print(f"Progress: {j.progress}%")
    print(f"Error: {j.error or 'Ninguno'}")
    
    # Print logs
    logs = JobLog.objects.filter(job=j).order_by('timestamp')
    print(f"\n=== LOGS ({logs.count()}) ===")
    for log in logs:
        print(f"  [{log.level}] {log.message}")
else:
    print("No hay jobs de download_users")

# Check users in DB
users = User.objects.all()
print(f"\n=== USUARIOS EN BD ===")
print(f"Total: {users.count()}")
for u in users[:10]:
    print(f"  UID={u.uid} | UserID={u.user_id} | Name={u.name} | Device={u.device_id}")
