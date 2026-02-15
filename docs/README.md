# 📚 DOCUMENTACIÓN SRTIME - Sistema de Gestión de Asistencia

**Proyecto**: SRTimeWeb (Django Backend + React Frontend)  
**Repositorio**: rauloar/srtime-django  
**Versión**: RC1.1 Beta Ready  
**Última Actualización**: 2026-02-12  

---

## 📋 ÍNDICE GENERAL

Esta carpeta contiene toda la documentación técnica, arquitectónica y funcional del sistema SRTimeWeb. Los documentos están organizados por categorías para facilitar la navegación.

### 🎯 Documentos de Entrada Rápida

| Documento | Descripción | Audiencia |
|-----------|-------------|-----------|
| [overview/README.md](overview/README.md) | Visión general del sistema | Todos |
| [overview/manual_uso_sistema.md](overview/manual_uso_sistema.md) | Manual de usuario | Usuarios finales |
| [arquitectura/TECHNICAL_HIERARCHY_ARCHITECTURE.md](arquitectura/TECHNICAL_HIERARCHY_ARCHITECTURE.md) | Arquitectura técnica completa | Developers |
| [api/endpoints-reference.md](api/endpoints-reference.md) | Referencia de API REST | Frontend/Integration |

---

## 🗂️ ESTRUCTURA DOCUMENTAL

### 📐 Arquitectura (7 documentos)

**Carpeta**: `arquitectura/`

Documentos sobre diseño, estructura y decisiones arquitectónicas del sistema.

| Documento | Descripción |
|-----------|-------------|
| [TECHNICAL_HIERARCHY_ARCHITECTURE.md](arquitectura/TECHNICAL_HIERARCHY_ARCHITECTURE.md) | Arquitectura técnica de jerarquía organizacional |
| [ENGINES_ASSESSMENT.md](arquitectura/ENGINES_ASSESSMENT.md) | Evaluación de motores de cálculo de asistencia |
| [FRONTEND_BACKEND_CONNECTIONS.md](arquitectura/FRONTEND_BACKEND_CONNECTIONS.md) | Conexiones entre frontend React y backend Django |
| [ASSESSMENT_SHIFTS_COMPLETO.txt](arquitectura/ASSESSMENT_SHIFTS_COMPLETO.txt) | Análisis completo del subsistema de turnos |
| [auditoria_alfa_time_attendance.md](arquitectura/auditoria_alfa_time_attendance.md) | Auditoría alfa del módulo time & attendance |
| [auditoria_frontend_backend_alpha.md](arquitectura/auditoria_frontend_backend_alpha.md) | Auditoría alfa de integración frontend-backend |
| [implementacion_visualizacion.md](arquitectura/implementacion_visualizacion.md) | Implementación del módulo de visualización |

**Temas clave**: Django ORM, React components, Database schema, API design, Calculation engines

---

### ✅ Auditorías y Validaciones (2 documentos)

**Carpeta**: `auditorias/`

Reportes de auditoría, validaciones y compliance del sistema.

| Documento | Descripción |
|-----------|-------------|
| [AUDIT.md](auditorias/AUDIT.md) | Auditoría general del sistema |
| [VALIDACION_SISTEMA.md](auditorias/VALIDACION_SISTEMA.md) | Validación completa del sistema RC1.0 |

**Temas clave**: Test coverage, Security checks, Code quality, Compliance

---

### 🔌 API y Endpoints (2 documentos)

**Carpeta**: `api/`

Documentación de la API REST del backend Django.

| Documento | Descripción |
|-----------|-------------|
| [endpoints-reference.md](api/endpoints-reference.md) | Referencia completa de endpoints REST |
| [MODAL_ENDPOINTS_TEST.md](api/MODAL_ENDPOINTS_TEST.md) | Tests de endpoints para modales |

**Endpoints principales**:
- `/api/v1/employees/` - Gestión de empleados
- `/api/v1/devices/` - Gestión de dispositivos biométricos
- `/api/v1/attendance/` - Registros de asistencia
- `/api/v1/schedules/` - Horarios y turnos
- `/api/v1/reports/` - Reportes y analytics

---

### 📖 Guías de Usuario (1 documento)

**Carpeta**: `guias/`

Manuales y guías para usuarios finales y administradores.

| Documento | Descripción |
|-----------|-------------|
| [GUIA_USUARIO_JERARQUIA_ORGANIZACIONAL.md](guias/GUIA_USUARIO_JERARQUIA_ORGANIZACIONAL.md) | Guía completa del módulo de jerarquía organizacional |

**Temas clave**: Companies, Positions, Departments, Zones, Employees

---

### 💾 Data Entry y Seeds (1 documento)

**Carpeta**: `data_entry/`

Documentación sobre datos iniciales, seeds y migraciones.

| Documento | Descripción |
|-----------|-------------|
| [seed_zktime_sql.md](data_entry/seed_zktime_sql.md) | Seeds SQL para datos de producción ZKTime |

**Temas clave**: Initial data, Production datasets, Test fixtures

---

### 📊 Análisis Técnicos (2 documentos)

**Carpeta**: `analisis/`

Análisis detallados de componentes específicos del sistema.

| Documento | Descripción |
|-----------|-------------|
| [reporte-ems-dashboard.md](analisis/reporte-ems-dashboard.md) | Análisis del dashboard EMS (versión 1) |
| [reporte-ems-dashboard-revisado.md](analisis/reporte-ems-dashboard-revisado.md) | Análisis del dashboard EMS (versión revisada) |

**Temas clave**: Dashboard components, Data visualization, UI/UX

---

### 🌐 Overview y Visión General (7 documentos)

**Carpeta**: `overview/`

Documentos de alto nivel sobre el sistema, reglas de oro y módulos principales.

| Documento | Descripción |
|-----------|-------------|
| [README.md](overview/README.md) | Overview principal del sistema |
| [README_overview.md](overview/README_overview.md) | Overview adicional (fusionado de 00_overview) |
| [manual_uso_sistema.md](overview/manual_uso_sistema.md) | Manual de uso general del sistema |
| [regla_de_oro_django_static.md](overview/regla_de_oro_django_static.md) | Regla de oro para archivos estáticos en Django |
| [visualization_module_complete.md](overview/visualization_module_complete.md) | Módulo de visualización completo |
| [visualization_module_summary.md](overview/visualization_module_summary.md) | Resumen del módulo de visualización |
| [testing_visualization_module.md](overview/testing_visualization_module.md) | Testing del módulo de visualización |

**Temas clave**: System overview, Best practices, Module documentation

---

### 📦 Producto y Decisiones (1 documento)

**Carpeta**: `producto/`

Decisiones de producto, funcionalidades y roadmap.

| Documento | Descripción |
|-----------|-------------|
| [product_attendance_decisions.md](producto/product_attendance_decisions.md) | Decisiones de producto para módulo de asistencia |

**Temas clave**: Product requirements, Feature decisions, Business logic

---

### 🧪 Testing y Resultados (4 documentos)

**Carpeta**: `testing/`

Resultados de ejecución de tests, coverage y validaciones.

| Documento | Descripción |
|-----------|-------------|
| [test_results.txt](testing/test_results.txt) | Resultados de tests (baseline) |
| [test_results_final.txt](testing/test_results_final.txt) | Resultados finales de tests |
| [test_results_final_v2.txt](testing/test_results_final_v2.txt) | Resultados finales v2 |
| [test_results_full.txt](testing/test_results_full.txt) | Resultados completos de test suite |

**Métricas actuales**: 147 PASSED / 8 SKIPPED / 0 FAILED

---

### 📜 Histórico (18 documentos)

**Carpeta**: `historico/`

Documentos históricos de fases previas del proyecto, auditorías antiguas y decisiones técnicas pasadas.

| Documento | Descripción |
|-----------|-------------|
| [AUDITORIA_ARQUITECTURA_FUNCIONAL.md](historico/AUDITORIA_ARQUITECTURA_FUNCIONAL.md) | Auditoría de arquitectura funcional (histórica) |
| [AUDITORIA_INFRAESTRUCTURA_TEST.md](historico/AUDITORIA_INFRAESTRUCTURA_TEST.md) | Auditoría de infraestructura de testing |
| [AUDITORIA_LOGICA_FICHAJE.md](historico/AUDITORIA_LOGICA_FICHAJE.md) | Auditoría de lógica de fichaje |
| [GOLDEN_RULE_CONFIRMED.txt](historico/GOLDEN_RULE_CONFIRMED.txt) | Confirmación de regla de oro arquitectónica |
| [PROJECT_COMPLETION_SUMMARY.txt](historico/PROJECT_COMPLETION_SUMMARY.txt) | Resumen de completitud del proyecto |
| [REFACTORING_COMPLETE.md](historico/REFACTORING_COMPLETE.md) | Reporte de refactoring completado |
| [TIMELINE_V1_CONTRACT.md](historico/TIMELINE_V1_CONTRACT.md) | Timeline del contrato v1.0 |
| [tree.txt](historico/tree.txt) | Estructura de árbol del proyecto |
| [freeze_2026-02-04.md](historico/freeze_2026-02-04.md) | Freeze del proyecto 2026-02-04 |
| [... y 9 documentos más](historico/) | Ver carpeta para listado completo |

**Nota**: Estos documentos son referencia histórica. Para información actual, consultar las carpetas principales.

---

### 🌍 Arquitectura Global y Contratos (29 documentos)

**Carpeta**: `arquitectura_global/`

📁 **Documentación Arquitectónica Global del Sistema SRTime**  
Contiene contratos formales, especificaciones técnicas, auditorías exhaustivas, reportes de implementación y análisis arquitectónicos completos del proyecto.

**📋 Índice Principal**: [arquitectura_global/README.md](arquitectura_global/README.md)  
**📚 Índice Maestro**: [arquitectura_global/INDICE_MAESTRO_DOCUMENTACION_ARQUITECTONICA.md](arquitectura_global/INDICE_MAESTRO_DOCUMENTACION_ARQUITECTONICA.md)

#### Subcarpetas:

| Categoría | Documentos | Descripción |
|-----------|------------|-------------|
| **[contratos/](arquitectura_global/contratos/)** | 1 | 🔒 Contrato operativo vinculante ZKTeco ↔ SRTimeWeb (RC1.1 Beta Ready) |
| **[especificaciones/](arquitectura_global/especificaciones/)** | 3 | 📐 Especificación formal de 5 flujos, checklist validación, propuestas de cambios |
| **[reportes/](arquitectura_global/reportes/)** | 5 | 📊 Reportes de implementación RC1.0/RC1.1, resúmenes ejecutivos |
| **[auditorias/](arquitectura_global/auditorias/)** | 3 | ✅ Auditorías exhaustivas pipeline asistencia, separación responsabilidades |
| **[analisis/](arquitectura_global/analisis/)** | 11 | 🔍 Análisis arquitectónicos frontend, backend, fullstack, motores de cálculo |
| **[fases/](arquitectura_global/fases/)** | 3 | 📅 Discovery histórico por fases del proyecto |

**Documentos clave**:
- 🔒 [CONTRATO_OPERATIVO_INTEGRACION_ZKTECO_SRTIMEWEB.md](arquitectura_global/contratos/CONTRATO_OPERATIVO_INTEGRACION_ZKTECO_SRTIMEWEB.md) - Contrato vinculante oficial
- 📐 [ESPECIFICACION_FORMAL_SRTIMEWEB_ZKTECO.md](arquitectura_global/especificaciones/ESPECIFICACION_FORMAL_SRTIMEWEB_ZKTECO.md) - 5 flujos operativos formales
- ✅ [CHECKLIST_VALIDACION_SRTIMEWEB.md](arquitectura_global/especificaciones/CHECKLIST_VALIDACION_SRTIMEWEB.md) - Validación exhaustiva (7 gaps cerrados)
- 🎯 [REPORTE_FINAL_IMPLEMENTACION_CONTRATO_RC1.1.md](arquitectura_global/reportes/REPORTE_FINAL_IMPLEMENTACION_CONTRATO_RC1.1.md) - RC1.1 Beta Ready (147/147 tests)

**Temas clave**: Contratos arquitectónicos, Principios rectores, Modelo de datos (21 tablas), Flujos operativos, Auditorías de compliance

---

## 🔍 BÚSQUEDA RÁPIDA POR TEMA

### Django Backend
- [arquitectura/TECHNICAL_HIERARCHY_ARCHITECTURE.md](arquitectura/TECHNICAL_HIERARCHY_ARCHITECTURE.md)
- [overview/regla_de_oro_django_static.md](overview/regla_de_oro_django_static.md)
- [api/endpoints-reference.md](api/endpoints-reference.md)

### React Frontend
- [arquitectura/FRONTEND_BACKEND_CONNECTIONS.md](arquitectura/FRONTEND_BACKEND_CONNECTIONS.md)
- [analisis/reporte-ems-dashboard-revisado.md](analisis/reporte-ems-dashboard-revisado.md)
- [overview/visualization_module_complete.md](overview/visualization_module_complete.md)

### Dispositivos Biométricos (ZKTeco)
- Ver documentación arquitectónica global: `c:\Proyectos\DOCUMENTACION_ARQUITECTONICA\`
- [CONTRATO_OPERATIVO_INTEGRACION_ZKTECO_SRTIMEWEB.md](../../DOCUMENTACION_ARQUITECTONICA/CONTRATO_OPERATIVO_INTEGRACION_ZKTECO_SRTIMEWEB.md)
- [ESPECIFICACION_FORMAL_SRTIMEWEB_ZKTECO.md](../../DOCUMENTACION_ARQUITECTONICA/ESPECIFICACION_FORMAL_SRTIMEWEB_ZKTECO.md)

### Testing
- [testing/test_results_final_v2.txt](testing/test_results_final_v2.txt)
- [overview/testing_visualization_module.md](overview/testing_visualization_module.md)
- [auditorias/VALIDACION_SISTEMA.md](auditorias/VALIDACION_SISTEMA.md)

### Módulo de Asistencia
- [arquitectura/ENGINES_ASSESSMENT.md](arquitectura/ENGINES_ASSESSMENT.md)
- [arquitectura/ASSESSMENT_SHIFTS_COMPLETO.txt](arquitectura/ASSESSMENT_SHIFTS_COMPLETO.txt)
- [producto/product_attendance_decisions.md](producto/product_attendance_decisions.md)

### Jerarquía Organizacional
- [guias/GUIA_USUARIO_JERARQUIA_ORGANIZACIONAL.md](guias/GUIA_USUARIO_JERARQUIA_ORGANIZACIONAL.md)
- [arquitectura/TECHNICAL_HIERARCHY_ARCHITECTURE.md](arquitectura/TECHNICAL_HIERARCHY_ARCHITECTURE.md)

---

## 📦 DOCUMENTACIÓN ARQUITECTÓNICA GLOBAL

La documentación arquitectónica principal del proyecto (análisis exhaustivos, contratos operativos, especificaciones formales) se encuentra en:

```
c:\Proyectos\DOCUMENTACION_ARQUITECTONICA\
```

**Documentos clave**:
- `CONTRATO_OPERATIVO_INTEGRACION_ZKTECO_SRTIMEWEB.md` - Contrato vinculante oficial RC1.1
- `ESPECIFICACION_FORMAL_SRTIMEWEB_ZKTECO.md` - Especificación técnica de 5 flujos
- `REPORTE_FINAL_IMPLEMENTACION_CONTRATO_RC1.1.md` - Reporte final de implementación
- `INDICE_MAESTRO_DOCUMENTACION_ARQUITECTONICA.md` - Índice maestro completo

---

## 🚀 GUÍA DE NAVEGACIÓN POR ROL

### Para Desarrolladores Backend
1. **Inicio**: [arquitectura/TECHNICAL_HIERARCHY_ARCHITECTURE.md](arquitectura/TECHNICAL_HIERARCHY_ARCHITECTURE.md)
2. **API**: [api/endpoints-reference.md](api/endpoints-reference.md)
3. **Motores**: [arquitectura/ENGINES_ASSESSMENT.md](arquitectura/ENGINES_ASSESSMENT.md)
4. **Tests**: [testing/test_results_final_v2.txt](testing/test_results_final_v2.txt)

### Para Desarrolladores Frontend
1. **Inicio**: [overview/visualization_module_complete.md](overview/visualization_module_complete.md)
2. **Conexiones**: [arquitectura/FRONTEND_BACKEND_CONNECTIONS.md](arquitectura/FRONTEND_BACKEND_CONNECTIONS.md)
3. **Dashboard**: [analisis/reporte-ems-dashboard-revisado.md](analisis/reporte-ems-dashboard-revisado.md)
4. **API**: [api/endpoints-reference.md](api/endpoints-reference.md)

### Para QA/Testing
1. **Inicio**: [auditorias/VALIDACION_SISTEMA.md](auditorias/VALIDACION_SISTEMA.md)
2. **Resultados**: [testing/test_results_final_v2.txt](testing/test_results_final_v2.txt)
3. **Módulos**: [overview/testing_visualization_module.md](overview/testing_visualization_module.md)

### Para Product Owners
1. **Inicio**: [overview/manual_uso_sistema.md](overview/manual_uso_sistema.md)
2. **Decisiones**: [producto/product_attendance_decisions.md](producto/product_attendance_decisions.md)
3. **Guía Usuario**: [guias/GUIA_USUARIO_JERARQUIA_ORGANIZACIONAL.md](guias/GUIA_USUARIO_JERARQUIA_ORGANIZACIONAL.md)

### Para Arquitectos
1. **Inicio Global**: [arquitectura_global/contratos/CONTRATO_OPERATIVO_INTEGRACION_ZKTECO_SRTIMEWEB.md](arquitectura_global/contratos/CONTRATO_OPERATIVO_INTEGRACION_ZKTECO_SRTIMEWEB.md)
2. **Índice Maestro**: [arquitectura_global/INDICE_MAESTRO_DOCUMENTACION_ARQUITECTONICA.md](arquitectura_global/INDICE_MAESTRO_DOCUMENTACION_ARQUITECTONICA.md)
3. **Sistema**: [arquitectura/TECHNICAL_HIERARCHY_ARCHITECTURE.md](arquitectura/TECHNICAL_HIERARCHY_ARCHITECTURE.md)
4. **Reportes RC1.1**: [arquitectura_global/reportes/](arquitectura_global/reportes/)
5. **Auditorías**: [auditorias/](auditorias/)

---

## 📊 ESTADÍSTICAS DE DOCUMENTACIÓN

- **Total de documentos**: 74 archivos (45 técnicos + 29 arquitectónicos)
- **Categorías principales**: 11 carpetas
- **Documentos de arquitectura técnica**: 7
- **Documentos de arquitectura global**: 29 (contratos, especificaciones, reportes, auditorías, análisis, fases)
- **Documentos históricos**: 18
- **Guías de usuario**: 1
- **Última reorganización**: 2026-02-12

---

## 🔄 HISTORIAL DE CAMBIOS

### 2026-02-12 - Reorganización Completa v2
- ✅ **FASE 1**: Documentos técnicos movidos desde raíz a `docs/` (8 archivos)
- ✅ **FASE 2**: Creadas carpetas temáticas: `auditorias/`, `guias/`, `testing/`
- ✅ **FASE 3**: Fusionada carpeta redundante `00_overview/` con `overview/`
- ✅ **FASE 4**: 45 documentos técnicos organizados en 10 categorías
- ✅ **FASE 5**: Documentación arquitectónica global movida de `c:\Proyectos\DOCUMENTACION_ARQUITECTONICA\` a `docs/arquitectura_global/`
- ✅ **FASE 6**: 29 documentos arquitectónicos organizados en 6 subcategorías (contratos, especificaciones, reportes, auditorias, analisis, fases)
- ✅ **RESULTADO**: 74 documentos totales, 11 categorías, estructura profesional completa
- ✅ Estructura limpia: 0 documentos sueltos en raíz de proyecto

### 2026-02-04 - Freeze Alfa
- Documentación inicial organizada por fases
- Estructura básica con overview, arquitectura, historico

---

## 🔗 ENLACES RELACIONADOS

- **Repositorio Principal**: https://github.com/rauloar/srtime-django
- **Documentación Arquitectónica Global**: `c:\Proyectos\DOCUMENTACION_ARQUITECTONICA\`
- **README Principal del Proyecto**: `../README.md`

---

## 📞 CONTRIBUIR A LA DOCUMENTACIÓN

Para mantener la documentación actualizada:

1. **Nuevos documentos**: Colocar en la carpeta apropiada según temática
2. **Actualizar índice**: Editar este README.md agregando el nuevo documento
3. **Nomenclatura**: 
   - Markdown: `nombre_descriptivo.md` (snake_case)
   - Reportes: `NOMBRE_REPORTE.md` o `NOMBRE_REPORTE.txt` (UPPERCASE)
4. **Formato**: Markdown (.md) preferido, TXT solo para logs/outputs
5. **Histórico**: Documentos obsoletos → mover a `historico/`

---

**Última Actualización**: 2026-02-12  
**Mantenedor**: Arquitecto Senior Backend + HR Systems Integration  
**Estado del Proyecto**: ✅ RC1.1 Beta Ready  
**Estado de Documentación**: ✅ Reorganización Completa
