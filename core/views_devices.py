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
from core.serializers import UserSerializer
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_device(request, device_id):
    """
    POST /api/v1/devices/{device_id}/restart/
    """
    device = get_object_or_404(models.Device, id=device_id)
    try:
        zk_service = get_zk_service(device.ip, device.port, timeout=5)
        result = zk_service.restart_device()
        return Response(result)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def poweroff_device(request, device_id):
    """
    POST /api/v1/devices/{device_id}/poweroff/
    """
    device = get_object_or_404(models.Device, id=device_id)
    try:
        zk_service = get_zk_service(device.ip, device.port, timeout=5)
        result = zk_service.poweroff_device()
        return Response(result)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_time(request, device_id):
    """
    POST /api/v1/devices/{device_id}/sync-time/
    """
    device = get_object_or_404(models.Device, id=device_id)
    try:
        zk_service = get_zk_service(device.ip, device.port, timeout=5)
        result = zk_service.sync_time()
        return Response(result)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_voice(request, device_id):
    """
    POST /api/v1/devices/{device_id}/test-voice/
    Query: voice_index (int)
    """
    device = get_object_or_404(models.Device, id=device_id)
    voice_index = int(request.query_params.get('voice_index', 0))
    try:
        zk_service = get_zk_service(device.ip, device.port, timeout=5)
        result = zk_service.test_voice(voice_index)
        return Response(result)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_memory_info(request, device_id):
    """
    GET /api/v1/devices/{device_id}/memory/
    """
    device = get_object_or_404(models.Device, id=device_id)
    try:
        zk_service = get_zk_service(device.ip, device.port, timeout=5)
        result = zk_service.get_memory_info()
        return Response(result)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_attendance(request, device_id):
    """
    GET /api/v1/devices/{device_id}/attendance/recent/
    Query: limit (int)
    """
    device = get_object_or_404(models.Device, id=device_id)
    limit = int(request.query_params.get('limit', 50))
    try:
        zk_service = get_zk_service(device.ip, device.port, timeout=10)
        result = zk_service.get_recent_attendance(limit=limit)
        return Response(result)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_device_templates(request, device_id):
    """
    POST /api/v1/devices/{device_id}/templates/
    Downloads templates from device and saves them to database
    """
    device = get_object_or_404(models.Device, id=device_id)
    try:
        zk_service = get_zk_service(device.ip, device.port, timeout=10)
        templates = zk_service.get_templates()
        
        saved_count = 0
        skipped_count = 0
        error_count = 0
        
        for t in templates:
            try:
                # Find user by uid AND device to ensure correct association
                user = models.User.objects.filter(device_id=device_id, uid=t.uid).first()
                if not user:
                    skipped_count += 1
                    continue
                
                # Determine template type based on fid (finger index)
                # fid 0-9 = fingers, 10+ could be face/palm
                template_type = 'FINGER' if t.fid < 10 else 'FACE'
                
                # Save or update template
                template, created = models.BiometricTemplate.objects.update_or_create(
                    user=user,
                    type=template_type,
                    index=t.fid,
                    defaults={
                        'valid': t.valid,
                        'data': str(t.template) if hasattr(t, 'template') else '',
                        'version': str(t.size) if hasattr(t, 'size') else None
                    }
                )
                saved_count += 1
            except Exception as e:
                error_count += 1
                continue
        
        return Response({
            "success": True, 
            "message": f"Templates guardados: {saved_count}, Omitidos (sin usuario): {skipped_count}, Errores: {error_count}", 
            "saved": saved_count,
            "skipped": skipped_count,
            "errors": error_count,
            "total": len(templates)
        })
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_device_info(request, device_id):
    """
    GET /api/v1/devices/{device_id}/info/
    """
    device = get_object_or_404(models.Device, id=device_id)
    try:
        zk_service = get_zk_service(device.ip, device.port, timeout=5)
        result = zk_service.get_info()
        return Response(result)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_device_users(request, device_id):
    try:
        # Check if device exists
        device = get_object_or_404(models.Device, pk=device_id)
        # Filter users for this device
        users = models.User.objects.filter(device=device)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    except Exception as e:
         return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
