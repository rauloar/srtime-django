"""
Device Operation Views
"""
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core import models
from core.services import get_zk_service, JobManager
from core.services.zk_workers import (
    run_test_connection_job,
    run_import_attendance_job,
    run_clear_attendance_job,
    run_download_users_job,
    run_sync_users_job,
    run_clear_all_data_job
)
import threading


def run_in_background(func, *args):
    """Helper to run job in background thread"""
    thread = threading.Thread(target=func, args=args, daemon=True)
    thread.start()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_connection(request, device_id):
    """
    POST /api/v1/devices/{device_id}/test-connection/
    """
    device = get_object_or_404(models.Device, id=device_id)
    
    # Create Job
    job = JobManager.create_job("test_connection", device_id=device_id)
    
    # Launch Background Task
    run_in_background(run_test_connection_job, job.id, device_id)
    
    return Response({
        "job_id": job.id,
        "status": "pending",
        "message": "Connection test started"
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_connection_sync(request, device_id):
    """
    GET /api/v1/devices/{device_id}/test-connection-sync/
    Fast synchronous connection test
    """
    device = get_object_or_404(models.Device, id=device_id)
    
    try:
        zk_service = get_zk_service(device.ip, device.port, timeout=5)
        result = zk_service.test_connection()
        return Response(result)
    except Exception as e:
        return Response({
            "success": False,
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_attendance(request, device_id):
    """
    POST /api/v1/devices/{device_id}/import-attendance/
    Body: {
        "overwrite": false,
        "start_date": "2025-01-01"  // Optional
    }
    """
    device = get_object_or_404(models.Device, id=device_id)
    
    overwrite = request.data.get('overwrite', False)
    start_date_str = request.data.get('start_date')
    
    start_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Create Job
    job = JobManager.create_job("import_attendance", device_id=device_id)
    
    # Launch Background Task
    run_in_background(run_import_attendance_job, job.id, device_id, overwrite, start_date)
    
    return Response({
        "job_id": job.id,
        "status": "pending",
        "message": "Attendance import started"
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_attendance(request, device_id):
    """
    POST /api/v1/devices/{device_id}/clear-attendance/
    """
    device = get_object_or_404(models.Device, id=device_id)
    
    # Create Job
    job = JobManager.create_job("clear_attendance", device_id=device_id)
    
    # Launch Background Task
    run_in_background(run_clear_attendance_job, job.id, device_id)
    
    return Response({
        "job_id": job.id,
        "status": "pending",
        "message": "Attendance clear started"
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def download_users(request, device_id):
    """
    POST /api/v1/devices/{device_id}/download-users/
    """
    device = get_object_or_404(models.Device, id=device_id)
    
    # Create Job
    job = JobManager.create_job("download_users", device_id=device_id)
    
    # Launch Background Task
    run_in_background(run_download_users_job, job.id, device_id)
    
    return Response({
        "job_id": job.id,
        "status": "pending",
        "message": "User download started"
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_users(request, device_id):
    """
    POST /api/v1/devices/{device_id}/sync-users/
    Body: {
        "employee_ids": [1, 2, 3]  // Optional, sync all if not provided
    }
    """
    device = get_object_or_404(models.Device, id=device_id)
    
    employee_ids = request.data.get('employee_ids')
    
    # Create Job
    job = JobManager.create_job("sync_users", device_id=device_id)
    
    # Launch Background Task
    run_in_background(run_sync_users_job, job.id, device_id, employee_ids)
    
    return Response({
        "job_id": job.id,
        "status": "pending",
        "message": "User sync started"
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_all_data(request, device_id):
    """
    POST /api/v1/devices/{device_id}/clear-all-data/
    WARNING: Deletes ALL users, fingerprints, and attendance records from device
    """
    device = get_object_or_404(models.Device, id=device_id)
    
    # Create Job
    job = JobManager.create_job("clear_all_data", device_id=device_id)
    
    # Launch Background Task
    run_in_background(run_clear_all_data_job, job.id, device_id)
    
    return Response({
        "job_id": job.id,
        "status": "pending",
        "message": "Clear all data started (WARNING: Destructive operation)"
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_devices_status(request):
    """
    GET /api/v1/devices/connection-status/all/
    Fast check for all devices
    """
    devices = models.Device.objects.all()
    status_list = []
    
    for device in devices:
        try:
            zk_service = get_zk_service(device.ip, device.port, timeout=3)
            result = zk_service.test_connection()
            status_list.append({
                "device_id": device.id,
                "name": device.name,
                "enabled": device.enabled,
                "connected": result.get("success", False),
                "message": result.get("message", "")
            })
        except Exception as e:
            status_list.append({
                "device_id": device.id,
                "name": device.name,
                "enabled": device.enabled,
                "connected": False,
                "message": str(e)
            })
    
    return Response({"devices": status_list})
