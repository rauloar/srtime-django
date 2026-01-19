# Scripts de Inicio - SRTime Django

Scripts PowerShell para facilitar el inicio del servidor Django y frontend React.

## ⚠️ IMPORTANTE: Primera Vez

Si obtienes el error **"la ejecución de scripts está deshabilitada"**, tienes 2 opciones:

### Opción 1: Script Automático (Recomendado)
```powershell
powershell -ExecutionPolicy Bypass -File .\setup-scripts.ps1
```

### Opción 2: Comando Manual
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
```

Esto permite ejecutar scripts locales sin requerir firma digital. Es **seguro** y solo afecta a tu usuario.

---

## 📋 Scripts Disponibles

### 🚀 `start-server.ps1`
Inicia únicamente el servidor Django en el puerto 9000.

```powershell
.\start-server.ps1
```

**Características:**
- ✅ Activa automáticamente el entorno virtual (.venv)
- ✅ Verifica la configuración de Django
- ✅ Inicia el servidor en `http://localhost:9000`
- ✅ Muestra mensajes informativos con colores

---

### 🛑 `stop-server.ps1`
Detiene todos los procesos del servidor Django corriendo en puerto 9000.

```powershell
.\stop-server.ps1
```

---

### 🎨 `start-frontend.ps1`
Inicia el servidor de desarrollo del frontend React+Vite.

```powershell
.\start-frontend.ps1
```

**Características:**
- ✅ Instala dependencias automáticamente si no existen
- ✅ Inicia Vite en modo desarrollo
- ✅ Disponible en `http://localhost:5173`

---

### 🔥 `start-all.ps1` (Recomendado)
Inicia backend y frontend en **ventanas separadas** simultáneamente.

```powershell
.\start-all.ps1
```

**Características:**
- ✅ Abre 2 ventanas PowerShell: una para backend, otra para frontend
- ✅ Espera 3 segundos entre inicios para que Django arranque primero
- ✅ Configuración lista para desarrollo

**URLs después de ejecutar:**
- Backend: http://localhost:9000
- Frontend: http://localhost:5173

---

## 🛠️ Requisitos

- PowerShell 5.1 o superior
- Python 3.11+ con entorno virtual configurado en `.venv`
- Node.js 18+ con dependencias instaladas en `frontend/`

---

## 📖 Uso Rápido

### Desarrollo Completo (Backend + Frontend)
```powershell
cd C:\Proyectos\srtime-django
.\start-all.ps1
```

### Solo Backend
```powershell
cd C:\Proyectos\srtime-django
.\start-server.ps1
```

### Solo Frontend
```powershell
cd C:\Proyectos\srtime-django
.\start-frontend.ps1
```

---

## ⚠️ Notas

1. **Política de Ejecución:** Si PowerShell no permite ejecutar scripts, ejecuta:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

2. **Puerto en Uso:** Si el puerto 9000 está ocupado, el script fallará. Detén procesos con:
   ```powershell
   .\stop-server.ps1
   ```

3. **Entorno Virtual:** El script `start-server.ps1` espera que `.venv` esté en el directorio raíz del proyecto.

---

## 🐛 Troubleshooting

### ⚠️ Error: "la ejecución de scripts está deshabilitada en este sistema"

**Causa:** PowerShell bloquea scripts por seguridad.

**Solución (RECOMENDADA - ejecutar una sola vez):**
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
```

**Alternativa sin cambiar política:**
```powershell
powershell -ExecutionPolicy Bypass -File .\start-server.ps1
```

**Verificar política actual:**
```powershell
Get-ExecutionPolicy -List
```

---

### Error: "No se puede cargar el archivo .ps1 porque la ejecución de scripts está deshabilitada"
**Solución:**
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
```

### Error: "python: command not found"
**Solución:** Asegúrate de que Python esté instalado y en el PATH del sistema.

### Error: "npm: command not found"
**Solución:** Instala Node.js desde https://nodejs.org/

---

## 📝 Logs y Debugging

Todos los scripts muestran output en tiempo real con colores:
- 🟢 Verde: Operaciones exitosas
- 🟡 Amarillo: Advertencias o procesos en curso
- 🔵 Cyan: Información general
- 🔴 Rojo: Errores

Para debug detallado, revisa:
- Backend logs: En la ventana del servidor Django
- Frontend logs: En la ventana de Vite
