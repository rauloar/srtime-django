"""
Script de prueba del sistema de logging.
Genera logs de ejemplo en todas las categorías para verificar funcionamiento.
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import logging

# Test all loggers
def test_logging_system():
    """Test all configured loggers with sample messages."""
    
    print("🧪 Probando sistema de logging...")
    print("=" * 70)
    
    # Test core logger
    print("\n1. Testing 'core' logger...")
    core_logger = logging.getLogger('core')
    core_logger.debug("DEBUG: Mensaje de depuración detallado")
    core_logger.info("INFO: Operación completada exitosamente")
    core_logger.warning("WARNING: Situación anómala detectada")
    core_logger.error("ERROR: Fallo en operación (simulado)")
    
    # Test attendance logger
    print("2. Testing 'attendance' logger...")
    attendance_logger = logging.getLogger('attendance')
    attendance_logger.info("Calculando asistencia para empleado A001")
    attendance_logger.debug("Turno resuelto: Administrativo, Horario: 08:00-17:00")
    
    # Test attendance.shadow logger
    print("3. Testing 'attendance.shadow' logger...")
    shadow_logger = logging.getLogger('attendance.shadow')
    shadow_logger.info("Shadow mode: V1 vs V2 validation")
    shadow_logger.warning("Discrepancia detectada: V1=480min, V2=475min")
    
    # Test API logger
    print("4. Testing 'api' logger...")
    api_logger = logging.getLogger('api')
    api_logger.info("→ GET /api/v1/employees/ | Status: 200 | Duration: 45ms")
    api_logger.warning("← POST /api/v1/employees/ | Status: 400 | Validation error")
    
    # Test devices logger
    print("5. Testing 'devices' logger...")
    devices_logger = logging.getLogger('devices')
    devices_logger.info("Conectando a dispositivo 192.168.1.100:4370")
    devices_logger.error("Error de conexión con dispositivo (simulado)")
    
    # Test exception logging with traceback
    print("6. Testing exception logging with traceback...")
    try:
        # Simulate an error
        result = 10 / 0
    except Exception as e:
        core_logger.error("Error simulado para demostrar captura de traceback", exc_info=True)
    
    print("\n" + "=" * 70)
    print("✅ Test completado!")
    print("\nRevisa los siguientes archivos en el directorio 'logs/':")
    print("  - django.log       → Logs generales (INFO+)")
    print("  - errors.log       → Solo errores (ERROR+)")
    print("  - attendance.log   → Motor de asistencia (DEBUG+)")
    print("  - api.log          → Requests/Responses (INFO+)")
    print("\nPara ver logs en tiempo real:")
    print("  Get-Content -Path logs\\errors.log -Wait -Tail 20")
    print("  Get-Content -Path logs\\api.log -Wait -Tail 20")


if __name__ == '__main__':
    test_logging_system()
