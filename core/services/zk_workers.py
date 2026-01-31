"""
ZK Device Workers - Adaptado para Django ORM
Workers para operaciones asíncronas con dispositivos biométricos
"""
from datetime import datetime, date
from typing import Optional
from django.db import transaction
from core import models
from .zk import get_zk_service
from .jobs import JobManager


def run_test_connection_job(job_id: str, device_id: int):
    """
    Worker para probar la conexión con un dispositivo
    """
    try:
        JobManager.start_job(job_id)
        JobManager.append_log(job_id, "Iniciando prueba de conexión...")
        
        device = models.Device.objects.get(id=device_id)
        JobManager.set_progress(job_id, 20, f"Conectando a {device.ip}:{device.port}...")
        
        zk_service = get_zk_service(device.ip, device.port, timeout=5)
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
    Worker para importar registros de asistencia desde un dispositivo
    """
    try:
        JobManager.start_job(job_id)
        JobManager.append_log(job_id, "Iniciando importación de registros...")
        
        device = models.Device.objects.get(id=device_id)
        JobManager.set_progress(job_id, 10, f"Conectando a {device.ip}:{device.port}...")
        
        zk_service = get_zk_service(device.ip, device.port, timeout=10)
        
        # Connect and Disable
        try:
            zk_service.connect()
            JobManager.append_log(job_id, "Deshabilitando terminal para operación segura...")
            zk_service.disable_device()
        except Exception as e:
            JobManager.finish_job(job_id, "failed", f"Error de conexión/inicio: {str(e)}")
            return

        try:
            JobManager.set_progress(job_id, 20, "Descargando registros del dispositivo...")
            
            # Get attendance records
            records = zk_service.get_attendance()
            
            if not records:
                JobManager.finish_job(job_id, "completed")
                JobManager.append_log(job_id, "No se encontraron registros nuevos")
                return
            
            JobManager.append_log(job_id, f"Descargados {len(records)} registros")
            JobManager.set_progress(job_id, 50, "Procesando registros...")
            
            imported_count = 0
            skipped_count = 0
            total = len(records)
            
            for idx, att in enumerate(records):
                # Progress update
                if idx % 100 == 0:
                    progress = 50 + int((idx / total) * 40)
                    JobManager.set_progress(job_id, progress)
                
                # Filter by start_date if provided
                if start_date and att.timestamp.date() < start_date:
                    skipped_count += 1
                    continue
                
                # Check if exists (skip duplicates unless overwrite=True)
                exists = models.AttendanceLog.objects.filter(
                    device_id=device_id,
                    user_id=att.user_id,
                    timestamp=att.timestamp
                ).exists()
                
                if exists and not overwrite:
                    skipped_count += 1
                    continue
                
                # Create or update
                if overwrite and exists:
                    models.AttendanceLog.objects.filter(
                        device_id=device_id,
                        user_id=att.user_id,
                        timestamp=att.timestamp
                    ).update(
                        status=att.status,
                        punch=att.punch,
                        verify_mode=1
                    )
                else:
                    models.AttendanceLog.objects.create(
                        device_id=device_id,
                        user_id=att.user_id,
                        timestamp=att.timestamp,
                        status=att.status,
                        punch=att.punch,
                        verify_mode=1
                    )
                
                imported_count += 1
            
            JobManager.set_progress(job_id, 95, "Finalizando...")
            JobManager.append_log(job_id, f"Registros importados: {imported_count}")
            JobManager.append_log(job_id, f"Registros omitidos: {skipped_count}")
            JobManager.finish_job(job_id, "completed")
        except Exception as e:
            JobManager.finish_job(job_id, "failed", f"Error durante procesamiento: {str(e)}")
        finally:
            # Always Enable and Disconnect
            try:
                JobManager.append_log(job_id, "Habilitando terminal...")
                zk_service.enable_device()
            except:
                pass
            zk_service.disconnect()
    
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
        
        zk_service = get_zk_service(device.ip, device.port, timeout=10)
        
        # Connect and Disable
        try:
            zk_service.connect()
            JobManager.append_log(job_id, "Deshabilitando terminal para operación segura...")
            zk_service.disable_device()
        except Exception as e:
            JobManager.finish_job(job_id, "failed", f"Error de conexión/inicio: {str(e)}")
            return

        try:
            JobManager.set_progress(job_id, 40, "Limpiando registros del dispositivo...")
            result = zk_service.clear_attendance()
            
            if result:
                JobManager.set_progress(job_id, 80, "Registros eliminados exitosamente")
                JobManager.finish_job(job_id, "completed")
            else:
                JobManager.finish_job(job_id, "failed", "No se pudo limpiar los registros")
        except Exception as e:
            JobManager.finish_job(job_id, "failed", f"Error durante limpieza: {str(e)}")
        finally:
             # Always Enable and Disconnect
            try:
                JobManager.append_log(job_id, "Habilitando terminal...")
                zk_service.enable_device()
            except:
                pass
            zk_service.disconnect()
    
    except Exception as e:
        JobManager.finish_job(job_id, "failed", str(e))


def run_download_users_job(job_id: str, device_id: int):
    """
    Worker para descargar usuarios desde un dispositivo
    """
    try:
        JobManager.start_job(job_id)
        JobManager.append_log(job_id, "Iniciando descarga de usuarios...")
        
        device = models.Device.objects.get(id=device_id)
        JobManager.set_progress(job_id, 10, f"Conectando a {device.ip}:{device.port}...")
        
        zk_service = get_zk_service(device.ip, device.port, timeout=10)
        
        # Connect and Disable
        try:
            zk_service.connect()
            JobManager.append_log(job_id, "Deshabilitando terminal para operación segura...")
            zk_service.disable_device()
        except Exception as e:
            JobManager.finish_job(job_id, "failed", f"Error de conexión/inicio: {str(e)}")
            return

        try:
            JobManager.set_progress(job_id, 20, "Descargando usuarios...")
            users = zk_service.get_users()
            
            if not users:
                JobManager.finish_job(job_id, "completed")
                JobManager.append_log(job_id, "No se encontraron usuarios")
                return
            
            JobManager.append_log(job_id, f"Descargados {len(users)} usuarios")
            JobManager.set_progress(job_id, 50, "Descargando plantillas de huellas...")
            
            # Get fingerprint templates
            templates = zk_service.get_templates()
            
            JobManager.append_log(job_id, f"Descargadas {len(templates)} plantillas de huellas")
            JobManager.set_progress(job_id, 80, "Procesando datos...")
            
            # Here you could create/update Employee records if needed
            # For now, just log the information
            
            JobManager.append_log(job_id, f"Total usuarios: {len(users)}")
            JobManager.append_log(job_id, f"Total plantillas: {len(templates)}")
            JobManager.finish_job(job_id, "completed")
        except Exception as e:
            JobManager.finish_job(job_id, "failed", f"Error durante descarga: {str(e)}")
        finally:
             # Always Enable and Disconnect
            try:
                JobManager.append_log(job_id, "Habilitando terminal...")
                zk_service.enable_device()
            except:
                pass
            zk_service.disconnect()
    
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
        
        zk_service = get_zk_service(device.ip, device.port, timeout=10)
        
        # Connect and Disable
        try:
            zk_service.connect()
            JobManager.append_log(job_id, "Deshabilitando terminal para operación segura...")
            zk_service.disable_device()
        except Exception as e:
            JobManager.finish_job(job_id, "failed", f"Error de conexión/inicio: {str(e)}")
            return

        try:
            JobManager.set_progress(job_id, 40, "Limpiando todos los datos del dispositivo...")
            result = zk_service.clear_all_data()
            
            if result:
                JobManager.set_progress(job_id, 80, "Todos los datos eliminados exitosamente")
                JobManager.append_log(job_id, "Dispositivo limpio - usuarios, huellas y registros eliminados")
                JobManager.finish_job(job_id, "completed")
            else:
                JobManager.finish_job(job_id, "failed", "No se pudo limpiar el dispositivo")
        except Exception as e:
             JobManager.finish_job(job_id, "failed", f"Error durante limpieza total: {str(e)}")
        finally:
             # Always Enable and Disconnect
            try:
                JobManager.append_log(job_id, "Habilitando terminal...")
                zk_service.enable_device()
            except:
                pass
            zk_service.disconnect()
    
    except Exception as e:
        JobManager.finish_job(job_id, "failed", str(e))


def run_sync_users_job(job_id: str, device_id: int, employee_ids: Optional[list] = None):
    """
    Worker para sincronizar usuarios al dispositivo
    """
    try:
        JobManager.start_job(job_id)
        JobManager.append_log(job_id, "Iniciando sincronización de usuarios...")
        
        device = models.Device.objects.get(id=device_id)
        JobManager.set_progress(job_id, 10, f"Conectando a {device.ip}:{device.port}...")
        
        zk_service = get_zk_service(device.ip, device.port, timeout=10)
        
        # Connect and Disable
        try:
            zk_service.connect()
            JobManager.append_log(job_id, "Deshabilitando terminal para operación segura...")
            zk_service.disable_device()
        except Exception as e:
            JobManager.finish_job(job_id, "failed", f"Error de conexión/inicio: {str(e)}")
            return

        try:
            JobManager.set_progress(job_id, 20, "Obteniendo empleados...")
            
            # Get employees to sync
            if employee_ids:
                employees = models.Employee.objects.filter(id__in=employee_ids, active=True)
            else:
                employees = models.Employee.objects.filter(active=True)
            
            employees = list(employees)
            total = len(employees)
            
            if total == 0:
                JobManager.finish_job(job_id, "completed")
                JobManager.append_log(job_id, "No hay empleados para sincronizar")
                return
            
            JobManager.append_log(job_id, f"Sincronizando {total} empleados...")
            
            synced_count = 0
            failed_count = 0
            
            for idx, emp in enumerate(employees):
                # Progress update
                progress = 20 + int((idx / total) * 70)
                JobManager.set_progress(job_id, progress)
                
                try:
                    # Set user to device
                    # Note: Using reuse connection
                    result = zk_service.set_user(
                        uid=int(emp.user_id) if emp.user_id else emp.id,
                        name=f"{emp.first_name} {emp.last_name}",
                        privilege=0,  # User level
                        password='',
                        group_id='0',
                        user_id=emp.user_id or str(emp.id),
                        card=0
                    )
                    
                    if result:
                        synced_count += 1
                    else:
                        failed_count += 1
                        JobManager.append_log(job_id, f"Error sincronizando: {emp.first_name} {emp.last_name}")
                
                except Exception as e:
                    failed_count += 1
                    JobManager.append_log(job_id, f"Error con {emp.first_name}: {str(e)}")
            
            JobManager.set_progress(job_id, 95, "Finalizando...")
            JobManager.append_log(job_id, f"Empleados sincronizados: {synced_count}")
            JobManager.append_log(job_id, f"Empleados fallidos: {failed_count}")
            JobManager.finish_job(job_id, "completed")
        except Exception as e:
             JobManager.finish_job(job_id, "failed", f"Error durante sincronización: {str(e)}")
        finally:
             # Always Enable and Disconnect
            try:
                JobManager.append_log(job_id, "Habilitando terminal...")
                zk_service.enable_device()
            except:
                pass
            zk_service.disconnect()
    
    except Exception as e:
        JobManager.finish_job(job_id, "failed", str(e))
