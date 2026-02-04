🎯 REGLA DE ORO - VERSIÓN ALFA CONGELADA
===============================================

React es ESTÁTICO dentro de Django
El frontend corre CON el runserver de Django
NO con npm run dev (eso es solo para desarrollo local)

═══════════════════════════════════════════════════════════════════════════

📋 FLUJO CORRECTO DE TRABAJO

1️⃣ EN DESARROLLO
   • Editar archivos en frontend/src/
   • npm run dev (para probar cambios rápido)
   • Pero ESTO NO ES PRODUCCIÓN

2️⃣ ANTES DE CONGELAR / PRODUCCIÓN
   • npm run build (compila React a archivos estáticos)
   • Los archivos van a: frontend/../static/
   • Django sirve estos archivos estáticos
   • python manage.py runserver (ÚNICO servidor)

3️⃣ EN PRODUCCIÓN (Versión Alfa)
   • Solo ejecutar: python manage.py runserver 127.0.0.1:9000
   • Django sirve:
     - API en /api/v1/
     - Frontend estático (React) en /
   • TODO en UN SOLO puerto

═══════════════════════════════════════════════════════════════════════════

✅ PASOS PARA PREPARAR ALFA CONGELADA

1. Compilar el frontend
   cd C:\Proyectos\srtime-django\frontend
   npm run build

   Resultado: archivos estáticos en static/

2. Verificar que Django serve los estáticos
   - settings.py tiene STATIC_URL = '/static/'
   - STATIC_ROOT apunta a la carpeta correcta
   - collectstatic ejecutado si es necesario

3. Iniciar solo Django
   cd C:\Proyectos\srtime-django
   python manage.py runserver 127.0.0.1:9000

4. Acceder
   http://127.0.0.1:9000/
   
   Django sirve:
   - / → index.html (React)
   - /api/v1/ → API endpoints
   - /static/ → CSS, JS, assets

═══════════════════════════════════════════════════════════════════════════

⚠️ IMPORTANTE

NO HACER:
   ❌ npm run dev (devserver separado)
   ❌ npm run preview
   ❌ Dos puertos diferentes (5173 + 9000)
   ❌ Acceder a localhost:5173

HACER:
   ✅ npm run build (compilar a estáticos)
   ✅ python manage.py runserver (UN servidor)
   ✅ http://127.0.0.1:9000 (UN puerto)
   ✅ Django sirve todo

═══════════════════════════════════════════════════════════════════════════

📁 ESTRUCTURA FINAL

C:\Proyectos\srtime-django\
├── manage.py
├── config/
│   ├── settings.py
│   └── urls.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── static/                    ← Aquí van los archivos compilados
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
└── core/
    └── (API endpoints)

Flujo:
   frontend/src/*.tsx
        ↓
   npm run build
        ↓
   static/ (archivos compilados)
        ↓
   python manage.py runserver
        ↓
   Django sirve / (index.html)
   Django sirve /api/v1/ (endpoints)

═══════════════════════════════════════════════════════════════════════════

🔧 VERIFICACIÓN

Ejecutar:
   cd C:\Proyectos\srtime-django\frontend
   npm run build

Verificar que se cree carpeta:
   ✅ static/index.html (existe)
   ✅ static/js/*.js (archivos compilados)
   ✅ static/css/*.css (estilos compilados)

Si esto existe, entonces:
   python manage.py runserver 127.0.0.1:9000

Acceder:
   http://127.0.0.1:9000/
   
   Debe mostrar la aplicación React completa

═══════════════════════════════════════════════════════════════════════════

✨ CONFIGURACIÓN ACTUAL (CORRECTA)

vite.config.ts:
   build: {
       outDir: '../static',      ← Compila AQUÍ
       emptyOutDir: true,
   }

package.json:
   "build": "tsc -b && vite build"  ← Script correcto

settings.py (Django):
   STATIC_URL = '/static/'
   STATIC_ROOT = 'static'

urls.py (Django):
   path('api/v1/', include(...))    ← APIs
   # React maneja el resto (index.html para SPA)

═══════════════════════════════════════════════════════════════════════════

🚀 PROCESO COMPLETO VERSIÓN ALFA

1. Desarrollo local (rápido)
   npm run dev

2. Preparar producción
   npm run build

3. Ejecutar producción (Alfa)
   python manage.py runserver 127.0.0.1:9000

4. Verificar
   Abrir http://127.0.0.1:9000/employees
   Debe funcionar sin servicio de desarrollo

5. Congelar
   git add static/
   git commit -m "freeze: compile frontend to static files"

═══════════════════════════════════════════════════════════════════════════

⭐ RESULTADO FINAL

TODO corre en UN ÚNICO servidor:
   • Solo python manage.py runserver
   • Un solo puerto (9000)
   • Django sirve todo (API + Frontend)
   • Frontend es ESTÁTICO (no se recalcula)

═══════════════════════════════════════════════════════════════════════════

REGLA DE ORO CONFIRMADA ✅

"React es estático dentro de Django
 y corre con el runserver de Django"

═══════════════════════════════════════════════════════════════════════════