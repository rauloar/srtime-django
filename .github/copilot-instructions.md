# Copilot instructions for SRTime Django

## Big picture
- Django REST backend + React/Vite frontend for attendance and HR management. Backend serves API under /api/v1 and can serve built frontend assets. See config/settings.py and frontend/.
- Business logic lives in core/services/ (attendance engine, schedule resolution, device integration). Views in core/views_*.py call the service layer.
- ZKTeco device operations are async “jobs” backed by Job and JobLog models. API endpoints create a job, then a background thread runs a worker that updates progress/logs.

## Key flows and patterns
- Attendance calculation: core/views_attendance.py -> core/services/attendance_engine.py. Schedule priority is Override -> Employee shift -> Department shift; daily schedule_type is derived from source + flexible/fixed.
- Device operations: core/views_devices.py -> core/services/zk_workers.py -> core/services/zk.py (pyzk wrapper). Workers follow Connect -> Disable -> Work -> Enable -> Disconnect for safety.
- Job tracking: use JobManager in core/services/jobs.py for status, progress, and log entries.

## Developer workflows (Windows/PowerShell)
- Recommended dev start: start-all.ps1 opens backend + frontend terminals. start-server.ps1 and start-frontend.ps1 are also available. See SCRIPTS_README.md.
- Backend: python manage.py runserver 0.0.0.0:9000 (default port in config/settings.py).
- Frontend: cd frontend && npm install && npm run dev (Vite on 5173). VITE_API_BASE_URL in frontend/.env.development.

## Testing conventions
- Ad-hoc scripts live in tests/ (python tests/<script>.py). See tests/README.md for what each script covers.
- Pytest is used for user endpoint tests (pytest tests/test_user_endpoints.py).
- Playwright is used for browser flow testing (tests/test_browser_flow.py).

## Integration points
- pyzk library for ZKTeco device I/O (core/services/zk.py).
- PostgreSQL settings are loaded from .env in config/settings.py (POSTGRES_* variables).
- Frontend expects API paths mapped in MAPEO_ENDPOINTS.md; keep response JSON compatible with the legacy frontend.

## When changing behavior
- Attendance logic changes should update both core/services/attendance_engine.py and any related endpoint expectations in MAPEO_ENDPOINTS.md.
- New device actions should follow existing worker + JobManager patterns to preserve job tracking and safety behavior.