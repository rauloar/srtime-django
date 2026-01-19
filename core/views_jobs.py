"""
Job Management Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core import models
from core.serializers import JobSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job(request, job_id):
    """
    GET /api/v1/jobs/{job_id}/
    """
    job = get_object_or_404(models.Job, id=job_id)
    serializer = JobSerializer(job)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_logs(request, job_id):
    """
    GET /api/v1/jobs/{job_id}/logs/
    """
    job = get_object_or_404(models.Job, id=job_id)
    
    # Get all logs for this job
    logs = models.JobLog.objects.filter(job=job).order_by('timestamp')
    log_output = "\n".join([f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log.message}" for log in logs])
    
    return Response({
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "log_output": log_output
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_device_jobs(request, device_id):
    """
    GET /api/v1/devices/{device_id}/jobs/
    """
    limit = int(request.query_params.get('limit', 10))
    
    jobs = models.Job.objects.filter(
        device_id=device_id
    ).order_by('-created_at')[:limit]
    
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)
