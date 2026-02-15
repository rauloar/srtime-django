"""Test sync users job"""
import time
import threading
from core.models import Job, User, JobLog
from core.services.jobs import JobManager
from core.services.zk_workers import run_sync_users_job

# Check users first
user_count = User.objects.count()
print(f"Usuarios en BD para sincronizar: {user_count}")
if user_count == 0:
    print("WARNING: No hay usuarios en BD. El job terminará rápido.")

# Create job
job = JobManager.create_job("sync_users", device_id=1)
print(f"Job creado ID: {job.id}")

# Run in separate thread context (simulating background)
print("Iniciando worker...")
try:
    # Run synchronously to see output immediately in script, 
    # but worker is designed to run in thread.
    run_sync_users_job(job.id, 1, user_ids=None)
    print("Worker finalizado.")
except Exception as e:
    print(f"Worker falló: {e}")

# Check final status
j = Job.objects.get(id=job.id)
print(f"Estado final: {j.status}")
print(f"Progreso: {j.progress}%")
print(f"Error: {j.error}")

print("\n=== LOGS ===")
for log in JobLog.objects.filter(job=j).order_by('timestamp'):
    print(f"[{log.level}] {log.message}")
