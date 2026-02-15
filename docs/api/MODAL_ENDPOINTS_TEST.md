# Test de Modales y Endpoints del Sistema

## Estado: ✅ CSRF Token Implementado

### Cambios Realizados:
1. ✅ Agregado CSRF token a todas las peticiones POST/PUT/PATCH/DELETE en `api.ts`
2. ✅ Configurado `withCredentials: true` en axios
3. ✅ Agregado endpoint `/api/v1/csrf/` para obtener el token
4. ✅ Configurado `CSRF_TRUSTED_ORIGINS` en settings.py
5. ✅ Agregado `useEffect` en App.tsx para obtener CSRF token al cargar

---

## Modales del Sistema y Endpoints que Utilizan

### 1. **Departamentos** (`/personnel/departments`)
**Modal:** DepartmentModal
- Endpoint: `POST /api/v1/departments/` (Crear)
- Endpoint: `PUT /api/v1/departments/{id}` (Actualizar)
- Endpoint: `DELETE /api/v1/departments/{id}` (Eliminar)
- **Endpoint NUEVO:** `POST /api/v1/employee-shifts/` (Asignar turno) ⚠️ **Este estaba fallando con 403**
- **Riesgo:** ALTO - Era el problema reportado
- **Test:** ✅ Debe poder asignar turno a departamento

### 2. **Empleados** (`/personnel/employees`)
**Modal:** EmployeeModal
- Endpoint: `POST /api/v1/employees/` (Crear)
- Endpoint: `PUT /api/v1/employees/{id}` (Actualizar)
- Endpoint: `DELETE /api/v1/employees/{id}` (Eliminar)
- Endpoint: `POST /api/v1/employees/import` (Importar desde Excel)
- **Riesgo:** ALTO - Operaciones CRUD frecuentes
- **Test:** ✅ Verificar crear/editar empleado

### 3. **Dispositivos** (`/devices`)
**Modal:** DeviceModal (en DeviceList)
- Endpoint: `POST /api/v1/devices/` (Crear)
- Endpoint: `PUT /api/v1/devices/{id}` (Actualizar)
- Endpoint: `DELETE /api/v1/devices/{id}` (Eliminar)
- Endpoint: `POST /api/v1/devices/{id}/test-connection/` (Test)
- Endpoint: `POST /api/v1/devices/{id}/import-attendance/` (Importar)
- Endpoint: `POST /api/v1/devices/{id}/sync-users/` (Sincronizar)
- **Riesgo:** CRÍTICO - Muchas operaciones POST
- **Test:** ✅ Verificar test de conexión y sincronización

### 4. **Horarios** (`/asistencia/timetables`)
**Modal:** TimetableModal
- Endpoint: `POST /api/v1/schedules/timetables/` (Crear)
- Endpoint: `PUT /api/v1/schedules/timetables/{id}` (Actualizar)
- Endpoint: `DELETE /api/v1/schedules/timetables/{id}` (Eliminar)
- **Riesgo:** MEDIO - Operaciones CRUD
- **Test:** ✅ Verificar crear/editar horario

### 5. **Turnos** (`/asistencia/shifts`)
**Modal:** ShiftModal + CycleModal
- Endpoint: `POST /api/v1/shifts/` (Crear)
- Endpoint: `DELETE /api/v1/shifts/{id}` (Eliminar)
- Endpoint: `POST /api/v1/shifts/{id}/timetables/` (Configurar ciclo)
- **Riesgo:** MEDIO - Configuración de ciclos puede fallar
- **Test:** ✅ Verificar crear turno y asignar horarios

### 6. **Asignación Individual** (`/asistencia/employee-schedule`)
**Modal:** ShiftAssignmentModal + BatchAssignmentModal
- Endpoint: `POST /api/v1/employee-shifts/` (Asignar turno individual o masivo)
- **Riesgo:** ALTO - Mismo endpoint que reportó error
- **Test:** ✅ Verificar asignación individual y masiva

### 7. **Posiciones** (`/organization/positions`)
**Modal:** PositionModal
- Endpoint: `POST /api/v1/positions/` (Crear)
- Endpoint: `PUT /api/v1/positions/{id}` (Actualizar)
- Endpoint: `DELETE /api/v1/positions/{id}` (Eliminar)
- **Riesgo:** BAJO - Operaciones simples
- **Test:** ✅ Verificar CRUD básico

### 8. **Zonas** (`/organization/zones`)
**Modal:** ZoneModal
- Endpoint: `POST /api/v1/zones/` (Crear)
- Endpoint: `PUT /api/v1/zones/{id}` (Actualizar)
- Endpoint: `DELETE /api/v1/zones/{id}` (Eliminar)
- **Riesgo:** BAJO - Operaciones simples
- **Test:** ✅ Verificar CRUD básico

### 9. **Logs de Asistencia** (`/logs`)
**Modal:** EditLogModal
- Endpoint: No hay POST/PUT desde el modal (solo lectura)
- **Riesgo:** NINGUNO - Solo lectura
- **Test:** ⚪ No requiere test

### 10. **Ausencias** (`/asistencia/absences`)
**Modal:** Inline modal
- Endpoint: `POST /api/v1/leaves/` (Crear ausencia)
- Endpoint: `DELETE /api/v1/leaves/{id}` (Eliminar ausencia)
- **Riesgo:** MEDIO - Operaciones CRUD
- **Test:** ✅ Verificar crear/eliminar ausencia

### 11. **Usuarios del Sistema** (`/system/users`) (Deshabilitado en DEV)
**Modal:** PasswordModal
- Endpoint: Auth deshabilitado en desarrollo
- **Riesgo:** NINGUNO - No activo
- **Test:** ⚪ Skip en desarrollo

---

## Plan de Testing Manual

### Prioridad CRÍTICA (Probar primero):
1. ✅ **Departamentos:** Editar departamento y asignar turno
2. ✅ **Asignación Individual:** Asignar turno a empleado
3. ✅ **Dispositivos:** Test de conexión

### Prioridad ALTA:
4. ✅ **Empleados:** Crear nuevo empleado
5. ✅ **Turnos:** Crear turno y configurar ciclo
6. ✅ **Horarios:** Crear nuevo horario

### Prioridad MEDIA:
7. ✅ **Ausencias:** Crear nueva ausencia
8. ✅ **Posiciones:** CRUD básico
9. ✅ **Zonas:** CRUD básico

---

## Verificación de CSRF Token

Para verificar que el CSRF token está funcionando correctamente:

1. Abrir DevTools (F12) → Network
2. Hacer cualquier operación POST/PUT/DELETE
3. Verificar en Headers:
   - ✅ Request Headers debe contener: `X-CSRFToken: xxxxx`
   - ✅ Cookies debe contener: `csrftoken=xxxxx`
4. Status Code debe ser **200** o **201** (no 403)

---

## Resultado Esperado

✅ **TODOS** los modales deben funcionar sin error 403
✅ El token CSRF se obtiene automáticamente al cargar la app
✅ Todas las peticiones POST/PUT/PATCH/DELETE incluyen el token

---

## Troubleshooting

Si aún hay error 403:
1. Verificar que el servidor Django está corriendo
2. Verificar que `/api/v1/csrf/` devuelve el token
3. Verificar en DevTools que la cookie `csrftoken` está presente
4. Verificar que `X-CSRFToken` header está en las peticiones
5. Limpiar cookies del navegador y recargar
