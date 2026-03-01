from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max
from core.models import Employee, DeviceUser, AttendanceLog


class Command(BaseCommand):
    help = "Preflight para migración Employee -> users (sin escribir datos)"

    def handle(self, *args, **options):
        employees = Employee.objects.count()
        users = DeviceUser.objects.count()
        logs = AttendanceLog.objects.count()

        self.stdout.write(self.style.NOTICE("=== PREFLIGHT Employee -> users ==="))
        self.stdout.write(f"Employees: {employees}")
        self.stdout.write(f"Users: {users}")
        self.stdout.write(f"AttendanceLog: {logs}")

        if employees == 0:
            self.stdout.write(self.style.SUCCESS("No hay Employee: no se requiere migración de datos."))
            return

        if users == 0:
            raise CommandError(
                "users está vacío. Ejecuta primero descarga/sync desde terminales (pyzk) para poblar users."
            )

        duplicated_user_ids = (
            DeviceUser.objects.exclude(user_id__isnull=True)
            .exclude(user_id="")
            .values("user_id")
            .annotate(c=Count("id"))
            .filter(c__gt=1)
        )

        if duplicated_user_ids.exists() and logs == 0:
            sample = list(duplicated_user_ids.values("user_id", "c")[:10])
            raise CommandError(
                "Hay user_id duplicados en users y no hay AttendanceLog para resolver terminal canónica. "
                f"Muestras: {sample}"
            )

        employees_without_user = (
            Employee.objects.exclude(user_id__isnull=True)
            .exclude(user_id="")
            .exclude(user_id__in=DeviceUser.objects.values_list("user_id", flat=True))
        )

        if employees_without_user.exists():
            sample = list(employees_without_user.values("id", "user_id")[:10])
            raise CommandError(
                "Hay Employee sin contraparte en users por user_id. "
                f"Muestras: {sample}"
            )

        if logs > 0:
            log_density = (
                AttendanceLog.objects.values("user_id")
                .annotate(
                    devices=Count("device_id", distinct=True),
                    last_ts=Max("timestamp"),
                )
                .filter(devices__gt=1)
            )
            self.stdout.write(
                f"User_id con fichadas en múltiples terminales: {log_density.count()}"
            )

        self.stdout.write(self.style.SUCCESS("Preflight OK: hay condiciones para mapear Employee -> users."))
