# SRTime-Django Test Scripts

Esta carpeta contiene scripts de prueba para verificar diferentes aspectos del sistema `srtime-django`. Los tests están organizados en pruebas unitarias, de integración, de API y E2E (End-to-End).

## 🚀 Guía Rápida

Para ejecutar la mayoría de los scripts (requiere entorno virtual activo):

```bash
python tests/nombre_del_script.py
```

Para los tests de pytest:
```bash
pytest tests/test_user_endpoints.py
```

---

## 📂 Listado de Scripts

### 🔍 Pruebas de API y Configuración

| Script | Descripción |
|--------|-------------|
| **`test_absences_api.py`** | Verifica el endpoint `/attendance/absences/`. Comprueba status 200 y estructura de respuesta. |
| **`test_attendance_config.py`** | **Start-to-Finish Workflow**: Realiza el flujo completo de configuración de asistencia: Login, creación de Horarios y Turnos, configuración de Ciclos y asignación a Empleados. |
| **`test_organization_api.py`** | Verifica la disponibilidad de los endpoints de organización básica: Companies, Positions y Zones. |
| **`test_updated_schema.py`** | Valida la estructura de los endpoints principales (Employees, Devices, Shifts, Attendance) asegurando que los campos esperados (ej. `mobile_phone`, `zone_rel`) estén presentes en la respuesta JSON. |
| **`test_logs_name.py`** | Comprobación específica para asegurar que el campo `user_name` se devuelve correctamente en el listado de logs de asistencia. |
| **`test_import.py`** | Verifica que los modelos y el motor de base de datos se pueden importar correctamente. Útil para debuggear problemas de entorno/paths. |

### 🧠 Pruebas de Lógica de Negocio (Motor de Asistencia)

| Script | Descripción |
|--------|-------------|
| **`test_unscheduled_work.py`** | **Unit Test**: Valida la lógica de cálculo de días (`calculate_day`). Cubre escenarios como "Día de Descanso", "Trabajo No Programado" y "Ausente". Usa base de datos en memoria (SQLite). |
| **`test_recalculation.py`** | **Integration Test**: Verifica la herencia de turnos (Departamento -> Empleado) y la lógica de recalculación. Prueba que modificar una asignación pasada actualiza correctamente los cálculos de asistencia. |
| **`test_override.py`** | **Integration Test**: Prueba la lógica de `resolve_schedule` para asegurar que las excepciones de horario (`ScheduleOverride`) tienen prioridad sobre los turnos normales. |
| **`test_device_safety_manual.py`** | **Unit Test (Mock)**: Verifica el "Modo Seguro" en la importación de datos. Asegura que el flujo `Connect -> Disable -> Get -> Enable -> Disconnect` se respeta, incluso si ocurre un error durante la descarga. |

### 🌐 Pruebas E2E y Frontend

| Script | Descripción |
|--------|-------------|
| **`test_browser_flow.py`** | **Playwright Test**: Simula un usuario real en el navegador. Realiza Login, navega al Dashboard, entra a un Dispositivo, y prueba los botones "Refrescar Info" y "Funciones Adicionales". |

### 🔐 Pruebas de Usuarios y Autenticación

| Script | Descripción |
|--------|-------------|
| **`test_user_endpoints.py`** | **Django Test (pytest)**: Prueba las operaciones CRUD (Crear, Leer, Actualizar, Borrar) para los usuarios de autenticación (`auth_users`) verificando permisos de administrador. |

---

## 🛠️ Notas de Ejecución

- **Entorno**: Asegúrate de tener activado el virtual environment (`.venv`).
- **Playwright**: Para `test_browser_flow.py`, necesitas haber instalado los navegadores (`playwright install`).
- **Base de Datos**: Los scripts de integración (`test_recalculation.py`, etc.) conectan a la base de datos configurada en `.env`. Ten cuidado de no ejecutarlos en producción si borran datos de prueba.
