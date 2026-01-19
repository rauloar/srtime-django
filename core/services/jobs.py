"""
Job Management System - Adaptado para Django ORM
Sistema de gestión de trabajos asíncronos para operaciones de dispositivos
"""
from datetime import datetime
from typing import Optional
import uuid
from django.db import transaction
from core import models


class JobManager:
    """
    Gestor de trabajos para operaciones asíncronas de dispositivos
    """
    
    @staticmethod
    def create_job(job_type: str, device_id: Optional[int] = None, user_id: Optional[int] = None) -> models.Job:
        """
        Crea un nuevo trabajo en estado pending
        """
        job = models.Job.objects.create(
            id=str(uuid.uuid4()),
            type=job_type,
            device_id=device_id,
            status="pending",
            progress=0
        )
        return job
    
    @staticmethod
    def start_job(job_id: str) -> models.Job:
        """
        Marca un trabajo como en ejecución
        """
        job = models.Job.objects.get(id=job_id)
        job.status = "running"
        job.started_at = datetime.now()
        job.save()
        return job
    
    @staticmethod
    def finish_job(job_id: str, status: str = "completed", error_message: Optional[str] = None) -> models.Job:
        """
        Finaliza un trabajo con éxito o error
        """
        job = models.Job.objects.get(id=job_id)
        job.status = status
        job.finished_at = datetime.now()
        job.progress = 100 if status == "completed" else job.progress
        
        if error_message:
            job.error = error_message
            JobManager.append_log(job_id, f"ERROR: {error_message}")
        
        job.save()
        return job
    
    @staticmethod
    def append_log(job_id: str, message: str) -> models.Job:
        """
        Añade un mensaje al log del trabajo
        """
        job = models.Job.objects.get(id=job_id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = models.JobLog.objects.create(
            job=job,
            timestamp=datetime.now(),
            message=message
        )
        return job
    
    @staticmethod
    def set_progress(job_id: str, progress: int, message: Optional[str] = None) -> models.Job:
        """
        Actualiza el progreso de un trabajo
        """
        job = models.Job.objects.get(id=job_id)
        job.progress = min(100, max(0, progress))
        
        if message:
            JobManager.append_log(job_id, message)
        
        job.save()
        return job
    
    @staticmethod
    def get_job(job_id: str) -> models.Job:
        """
        Obtiene un trabajo por ID
        """
        return models.Job.objects.get(id=job_id)
    
    @staticmethod
    def get_device_jobs(device_id: int, limit: int = 10) -> list:
        """
        Obtiene los últimos trabajos de un dispositivo
        """
        return list(models.Job.objects.filter(
            device_id=device_id
        ).order_by('-created_at')[:limit])
    
    @staticmethod
    def cleanup_old_jobs(days: int = 30):
        """
        Limpia trabajos antiguos completados
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = models.Job.objects.filter(
            status__in=['completed', 'failed'],
            finished_at__lt=cutoff_date
        ).delete()[0]
        
        return deleted_count
