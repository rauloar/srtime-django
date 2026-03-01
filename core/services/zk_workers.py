"""
ZK Device Workers - Adaptado para Django ORM
Workers para operaciones asíncronas con dispositivos biométricos

⚠️ LEGACY ZKTECO INTEGRATION
These workers directly persist AttendanceLog and couple device operations with data layer.
Do not extend or reuse for new features.

New ZKTeco integrations must implement data_entry.ZKTecoAdapter pattern:
  - Batch mode (connect -> disable -> download -> enable -> disconnect)
  - Returns raw data structures only
  - No direct persistence or business logic
  - Decoupled from async workers

This code remains operational but frozen for compatibility.

🔮 MULTI-BRAND ABSTRACTION (FUTURE - NOT IMPLEMENTED)
====================================================
When adding support for non-ZKTeco devices (e.g., Hikvision, Anviz, ZKFace):

ARCHITECTURE:
------------
1. Create DeviceAdapter interface in core/services/device_adapter.py:
   
   class DeviceAdapter(ABC):
       @abstractmethod
       def connect(self) -> None: pass
       
       @abstractmethod
       def disconnect(self) -> None: pass
       
       @abstractmethod
       def get_attendance(self) -> List[NormalizedAttendanceRecord]: pass
       
       @abstractmethod
       def set_user(self, uid, name, ...) -> bool: pass
       
       @abstractmethod
       def get_templates(self) -> List[NormalizedBiometricTemplate]: pass

2. Implement ZKTecoAdapter (refactor current ZKService):
   class ZKTecoAdapter(DeviceAdapter):
       # Wraps pyzk library

3. Update get_zk_service() to device_adapter_factory():
   def get_device_adapter(device_type: str, ip: str, port: int):
       if device_type == 'zkteco':
           return ZKTecoAdapter(ip, port)
       elif device_type == 'hikvision':
           return HikvisionAdapter(ip, port)
       # ...

4. Add device.device_type field to models.Device (migration required)

5. Update all workers to use:
   adapter = get_device_adapter(device.device_type, device.ip, device.port)

CURRENT STATE: Single-brand (ZKTeco), tightly coupled to pyzk.
MIGRATION PATH: See CONTRATO_OPERATIVO section 7 for full plan.
"""
import logging
from datetime import datetime, date
from typing import Optional
from django.db import transaction
from core import models
from .device_adapter_factory import get_device_adapter
from data_entry.zkteco_adapter import ZKTecoAdapterError
from .jobs import JobManager

logger = logging.getLogger(__name__)


def run_test_connection_job(job_id: str, device_id: int):
    """
    Worker para probar la conexión con un dispositivo
    """
    try:
        JobManager.start_job(job_id)
        JobManager.append_log(job_id, "Iniciando prueba de conexión...")
        
        device = models.Device.objects.get(id=device_id)
        JobManager.set_progress(job_id, 20, f"Conectando a {device.ip}:{device.port}...")
        
        zk_service = get_device_adapter(device, timeout=5)
        result = zk_service.test_connection()
        
        if result["success"]:
            JobManager.set_progress(job_id, 80, f"Conexión exitosa: {result['message']}")
            JobManager.append_log(job_id, f"Firmware: {result.get('firmware_version', 'N/A')}")
            JobManager.append_log(job_id, f"Serial: {result.get('serial_number', 'N/A')}")
            JobManager.append_log(job_id, f"Platform: {result.get('platform', 'N/A')}")
            JobManager.finish_job(job_id, "completed")
        else:
            JobManager.finish_job(job_id, "failed", f"Error de conexión: {result['message']}")
    
    except Exception as e:
        JobManager.finish_job(job_id, "failed", str(e))


def run_import_attendance_job(job_id: str, device_id: int, overwrite: bool = False, start_date: Optional[date] = None):
    """
    Worker para importar registros de asistencia desde un dispositivo ZKTeco.
    
    ARCHITECTURAL PRINCIPLE:
    ========================
    This function is PART OF THE ATTENDANCE INGESTION PIPELINE.
    It handles ONLY attendance record capture, NOT employee master data.
    
    HR SYSTEM IS SOURCE OF TRUTH:
    ============================
    - Employee records are maintained by HR system (RRHH) only
    - Device is NOT authoritative for employee data
    - If an employee is deleted from HR system, they remain in Device
    - User downloads from device (run_download_users_job) are for audit/informational only
    
    ✓ WHAT THIS FUNCTION DOES:
      - Downloads attendance records (punches) from ZKTeco device
      - Creates/updates AttendanceLog records in database
      - Handles deduplication via UNIQUE(device, user_id, timestamp)
      - Validates employee existence before creating records
    
    ✗ WHAT THIS FUNCTION DOES NOT DO:
      - Does NOT create Employee records
      - Does NOT modify Employee data (name, department, etc.)
      - Does NOT change HR master data
    
    EMPLOYEE SYNCHRONIZATION:
    ========================
    - Synchronization of Employee TO device: use run_sync_users_job()
    - Direction is always: HR System → Device (not reverse)
    """
    try:
        JobManager.start_job(job_id)
        JobManager.append_log(job_id, "Iniciando importación de registros...")
        
        device = models.Device.objects.get(id=device_id)
        JobManager.set_progress(job_id, 10, f"Conectando a {device.ip}:{device.port}...")
        
        adapter = get_device_adapter(device, timeout=10, mode="batch")

        try:
            JobManager.set_progress(job_id, 20, "Descargando registros del dispositivo...")
            records = adapter.fetch_attendance_batch()
            
            if not records:
                JobManager.finish_job(job_id, "completed")
                JobManager.append_log(job_id, "No se encontraron registros nuevos")
                return
            
            JobManager.append_log(job_id, f"Descargados {len(records)} registros")
            JobManager.set_progress(job_id, 50, "Procesando registros...")
            
            imported_count = 0
            skipped_count = 0
            invalid_employee_count = 0
            total = len(records)
            
            for idx, event in enumerate(records):
                # Progress update
                if idx % 100 == 0:
                    progress = 50 + int((idx / total) * 40)
                    JobManager.set_progress(job_id, progress)

                att_user_id = str(event.get("user_id") or "")
                att_timestamp = event.get("timestamp")
                att_status = int(event.get("status") or 0)
                att_punch = int(event.get("punch") or 0)

                if not att_user_id or not att_timestamp:
                    skipped_count += 1
                    continue
                
                # Filter by start_date if provided
                if start_date and att_timestamp.date() < start_date:
                    skipped_count += 1
                    continue
                
                # VALIDATION: Ensure employee exists in HR system
                # HR System is source of truth - we do NOT create employees from device
                try:
                    employee = models.Employee.objects.get(user_id=att_user_id)
                except models.Employee.DoesNotExist:
                    invalid_employee_count += 1
                    # Enhanced structured logging for debugging
                    logger.warning(
                        "Attendance skipped - Employee not found",
                        extra={
                            "device_id": device_id,
                            "user_id": att_user_id,
                            "timestamp": str(att_timestamp),
                            "source": "DEVICE"
                        }
                    )
                    JobManager.append_log(
                        job_id,
                        f"[SKIP] No employee for user_id='{att_user_id}'. "
                        f"HR system is source of truth. Sync device users first."
                    )
                    skipped_count += 1
                    continue
                
                # Check if exists (skip duplicates unless overwrite=True)
                exists = models.AttendanceLog.objects.filter(
                    device_id=device_id,
                    user_id=att_user_id,
                    timestamp=att_timestamp
                ).exists()
                
                if exists and not overwrite:
                    skipped_count += 1
                    continue
                
                # Create or update
                if overwrite and exists:
                    models.AttendanceLog.objects.filter(
                        device_id=device_id,
                        user_id=att_user_id,
                        timestamp=att_timestamp
                    ).update(
                        employee_id=employee.id,
                        status=att_status,
                        punch=att_punch,
                        verify_mode=1
                    )
                else:
                    models.AttendanceLog.objects.create(
                        device_id=device_id,
                        employee_id=employee.id,
                        user_id=att_user_id,
                        timestamp=att_timestamp,
                        status=att_status,
                        punch=att_punch,
                        verify_mode=1
                    )
                
                imported_count += 1
            
            JobManager.set_progress(job_id, 95, "Finalizando...")
            JobManager.append_log(job_id, f"Registros importados: {imported_count}")
            JobManager.append_log(job_id, f"Registros omitidos (duplicado/antes): {skipped_count}")
            if invalid_employee_count > 0:
                JobManager.append_log(
                    job_id,
                    f"⚠️ Registros rechazados (employee no existe): {invalid_employee_count} "
                    f"(HR system es source of truth)"
                )
            JobManager.append_log(
                job_id,
                f"Resumen: Importados={imported_count}, Omitidos={skipped_count}, "
                f"Sin_Empleado={invalid_employee_count}"
            )
            JobManager.finish_job(job_id, "completed")
        except ZKTecoAdapterError as e:
            JobManager.finish_job(job_id, "failed", f"Error de adapter ZKTeco: {str(e)}")
        except Exception as e:
            JobManager.finish_job(job_id, "failed", f"Error durante procesamiento: {str(e)}")
    
    except Exception as e:
        JobManager.finish_job(job_id, "failed", str(e))


def run_clear_attendance_job(job_id: str, device_id: int):
    """
    Worker para limpiar registros de asistencia de un dispositivo
    """
    try:
        JobManager.start_job(job_id)
        JobManager.append_log(job_id, "Iniciando limpieza de registros...")
        
        device = models.Device.objects.get(id=device_id)
        JobManager.set_progress(job_id, 10, f"Conectando a {device.ip}:{device.port}...")
        
        adapter = get_device_adapter(device, timeout=10, mode="batch")

        try:
            JobManager.set_progress(job_id, 40, "Limpiando registros del dispositivo...")
            result = adapter.clear_attendance_batch()
            
            if result:
                JobManager.set_progress(job_id, 80, "Registros eliminados exitosamente")
                JobManager.finish_job(job_id, "completed")
            else:
                JobManager.finish_job(job_id, "failed", "No se pudo limpiar los registros")
        except ZKTecoAdapterError as e:
            JobManager.finish_job(job_id, "failed", f"Error de adapter ZKTeco: {str(e)}")
        except Exception as e:
            JobManager.finish_job(job_id, "failed", f"Error durante limpieza: {str(e)}")
    
    except Exception as e:
        JobManager.finish_job(job_id, "failed", str(e))


def run_download_users_job(job_id: str, device_id: int):
    """
    Worker para descargar Y LOGGEAR usuarios desde un dispositivo ZKTeco.
    
    IMPORTANT: This is an AUDIT/INFORMATIONAL function.
    It does NOT create or modify Employee records.
    
    This function is used to:
    - Verify which users are currently enrolled on the device
    - Check biometric templates stored on device
    - Audit device state vs HR system
    
    HR SYSTEM IS SOURCE OF TRUTH:
    ============================
    Employee records come from HR system (RRHH module) only.
    Device is NOT used to create/update employees.
    
    NOTE: Downloading users from device does NOT modify any database.
    This is read-only audit information.
    """
    try:
        JobManager.start_job(job_id)
        JobManager.append_log(job_id, "Iniciando descarga de usuarios...")
        
        device = models.Device.objects.get(id=device_id)
        JobManager.set_progress(job_id, 10, f"Conectando a {device.ip}:{device.port}...")
        
        adapter = get_device_adapter(device, timeout=10, mode="batch")
        
        try:
            JobManager.set_progress(job_id, 20, "Descargando usuarios...")
            users = adapter.fetch_users_batch()
            
            if not users:
                JobManager.finish_job(job_id, "completed")
                JobManager.append_log(job_id, "No se encontraron usuarios")
                return
            
            JobManager.append_log(job_id, f"Descargados {len(users)} usuarios del dispositivo")
            JobManager.set_progress(job_id, 50, "Guardando usuarios en base de datos...")
            
            # Save users to database
            saved_count = 0
            updated_count = 0
            
            for user in users:
                # Handle integer fields - convert empty strings to None
                group_id_val = getattr(user, 'group_id', None)
                if group_id_val == '' or group_id_val == '0':
                    group_id_val = None
                
                privilege_val = user.privilege
                if privilege_val == '':
                    privilege_val = None
                    
                card_val = getattr(user, 'card', None)
                if card_val == '':
                    card_val = None
                
                obj, created = models.DeviceUser.objects.update_or_create(
                    device_id=device_id,
                    uid=user.uid,
                    defaults={
                        'name': user.name,
                        'privilege': privilege_val,
                        'password': user.password or '',
                        'group_id': group_id_val,
                        'user_id': user.user_id,
                        'card': card_val,
                    }
                )
                
                if created:
                    saved_count += 1
                else:
                    updated_count += 1
            
            JobManager.set_progress(job_id, 90, "Finalizando...")
            JobManager.append_log(job_id, f"Usuarios guardados: {saved_count}")
            JobManager.append_log(job_id, f"Usuarios actualizados: {updated_count}")
            JobManager.append_log(job_id, f"Total procesado: {saved_count + updated_count} usuarios")
            JobManager.finish_job(job_id, "completed")
        except ZKTecoAdapterError as e:
            JobManager.finish_job(job_id, "failed", f"Error de adapter ZKTeco: {str(e)}")
        except Exception as e:
            JobManager.finish_job(job_id, "failed", f"Error durante descarga: {str(e)}")
    
    except Exception as e:
        JobManager.finish_job(job_id, "failed", str(e))


def run_clear_all_data_job(job_id: str, device_id: int):
    """
    Worker para limpiar todos los datos de un dispositivo
    """
    try:
        JobManager.start_job(job_id)
        JobManager.append_log(job_id, "Iniciando limpieza completa de datos...")
        JobManager.append_log(job_id, "ADVERTENCIA: Se eliminarán TODOS los usuarios, huellas y registros")
        
        device = models.Device.objects.get(id=device_id)
        JobManager.set_progress(job_id, 10, f"Conectando a {device.ip}:{device.port}...")
        
        adapter = get_device_adapter(device, timeout=10, mode="batch")

        try:
            JobManager.set_progress(job_id, 40, "Limpiando todos los datos del dispositivo...")
            result = adapter.clear_all_data_batch()
            
            if result:
                JobManager.set_progress(job_id, 80, "Todos los datos eliminados exitosamente")
                JobManager.append_log(job_id, "Dispositivo limpio - usuarios, huellas y registros eliminados")
                JobManager.finish_job(job_id, "completed")
            else:
                JobManager.finish_job(job_id, "failed", "No se pudo limpiar el dispositivo")
        except ZKTecoAdapterError as e:
            JobManager.finish_job(job_id, "failed", f"Error de adapter ZKTeco: {str(e)}")
        except Exception as e:
             JobManager.finish_job(job_id, "failed", f"Error durante limpieza total: {str(e)}")
    
    except Exception as e:
        JobManager.finish_job(job_id, "failed", str(e))


def run_sync_users_job(job_id: str, device_id: int, user_ids: Optional[list] = None):
    """
    Worker para sincronizar usuarios desde la Base de Datos hacia el dispositivo ZKTeco.
    
    DATA FLOW UPDATE (2025):
    =======================
    Originalmente: Employee (HR) -> Device
    Actualmente: User (DB) -> Device
    
    Razón: La tabla 'employees' está vacía. La tabla 'users' actúa como espejo maestro
    de los usuarios descargados de los dispositivos.
    
    LOGIC:
    - Lee usuarios de la tabla 'users'
    - Si hay duplicados (mismo user_id en varios dispositivos), toma el más reciente
    - Envía comando set_user al dispositivo destino
    """
    try:
        JobManager.start_job(job_id)
        JobManager.append_log(job_id, "Iniciando sincronización de usuarios hacia terminal...")
        
        device = models.Device.objects.get(id=device_id)
        JobManager.set_progress(job_id, 10, f"Conectando a {device.ip}:{device.port}...")

        adapter = get_device_adapter(device, timeout=10, mode="batch")

        try:
            JobManager.set_progress(job_id, 20, "Obteniendo usuarios de la base de datos...")
            
            # Obtener usuarios únicos por user_id (tomando el más reciente si hay duplicados)
            from django.db.models import Max
            
            # 1. Identificar IDs de registros únicos (agrupados por user_id)
            if user_ids:
                # Si se especifican IDs, usarlos (asumiendo que el caller ya filtró)
                target_users_qs = models.DeviceUser.objects.filter(id__in=user_ids)
            else:
                # Si es sync total, obtener últimos registros de cada user_id
                latest_ids = models.DeviceUser.objects.values('user_id').annotate(max_id=Max('id')).values_list('max_id', flat=True)
                target_users_qs = models.DeviceUser.objects.filter(id__in=latest_ids)
            
            target_users = list(target_users_qs.order_by('user_id'))
            total = len(target_users)
            
            if total == 0:
                JobManager.finish_job(job_id, "completed")
                JobManager.append_log(job_id, "No hay usuarios para sincronizar en la base de datos")
                return
            
            JobManager.append_log(job_id, f"Sincronizando {total} usuarios...")

            payload = []
            for idx, user in enumerate(target_users):
                # Progress update
                progress = 20 + int((idx / total) * 30)
                JobManager.set_progress(job_id, progress)

                card_val = int(user.card) if user.card and str(user.card).isdigit() else 0
                payload.append({
                    "uid": user.uid,
                    "name": user.name,
                    "privilege": user.privilege if user.privilege is not None else 0,
                    "password": user.password or '',
                    "group_id": str(user.group_id) if user.group_id is not None else '0',
                    "user_id": user.user_id,
                    "card": card_val,
                })

            JobManager.set_progress(job_id, 55, "Sincronizando usuarios con el dispositivo...")
            sync_results = adapter.sync_users_batch(payload)

            synced_count = 0
            failed_count = 0
            for idx, result in enumerate(sync_results):
                progress = 55 + int(((idx + 1) / total) * 35)
                JobManager.set_progress(job_id, progress)

                if result.get("success"):
                    synced_count += 1
                else:
                    failed_count += 1
                    user_id_val = result.get("user_id") or "unknown"
                    error_msg = result.get("error") or "rejected by device"
                    JobManager.append_log(job_id, f"Error con {user_id_val}: {error_msg}")
            
            JobManager.set_progress(job_id, 95, "Finalizando...")
            JobManager.append_log(job_id, f"Usuarios sincronizados: {synced_count}")
            if failed_count > 0:
                JobManager.append_log(job_id, f"Usuarios fallidos: {failed_count}")
                
            JobManager.finish_job(job_id, "completed")
        except ZKTecoAdapterError as e:
            JobManager.finish_job(job_id, "failed", f"Error de adapter ZKTeco: {str(e)}")
        except Exception as e:
             JobManager.finish_job(job_id, "failed", f"Error durante sincronización: {str(e)}")

    except Exception as e:
        JobManager.finish_job(job_id, "failed", str(e))
