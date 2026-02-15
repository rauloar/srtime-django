"""
Job Management Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core import models
from core.serializers import JobSerializer


class JobAccessPermission(BasePermission):
    """Allow access to device_admin/admin_system groups or superusers."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True
        return user.groups.filter(name__in=['device_admin', 'admin_system']).exists()


@api_view(['GET'])
@permission_classes([IsAuthenticated, JobAccessPermission])
def get_job(request, job_id):
    """
    GET /api/v1/jobs/{job_id}/
    """
    job = get_object_or_404(models.Job, id=job_id)
    serializer = JobSerializer(job)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, JobAccessPermission])
def get_job_logs(request, job_id):
    """
    GET /api/v1/jobs/{job_id}/logs/
    """
    job = get_object_or_404(models.Job, id=job_id)
    
    # Get all logs for this job
    logs = models.JobLog.objects.filter(job=job).order_by('timestamp')
    
    # Return array of log objects (not concatenated string)
    log_array = [{
        "timestamp": log.timestamp.isoformat(),
        "message": log.message,
        "level": log.level
    } for log in logs]
    
    return Response(log_array)


@api_view(['GET'])
@permission_classes([IsAuthenticated, JobAccessPermission])
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
