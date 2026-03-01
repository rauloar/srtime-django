import json
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from core.models import AttendanceLog, Employee, DeviceUser


class Command(BaseCommand):
    help = "Resuelve mapeo Employee -> User usando user_id y terminal (device)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="",
            help="Ruta opcional para exportar mapping JSON",
        )

    def handle(self, *args, **options):
        output = options.get("output")

        users_by_user_id = defaultdict(list)
        for user in DeviceUser.objects.exclude(user_id__isnull=True).exclude(user_id=""):
            users_by_user_id[user.user_id].append(user)

        if not users_by_user_id:
            raise CommandError("users está vacío; no se puede resolver mapping.")

        top_device_by_user_id = {
            row["user_id"]: row["device_id"]
            for row in (
                AttendanceLog.objects.exclude(user_id__isnull=True)
                .exclude(user_id="")
                .values("user_id", "device_id")
                .annotate(c=Count("id"))
                .order_by("user_id", "-c", "device_id")
            )
            if row["user_id"] not in locals().get("_seen", set())
            for _seen in [locals().setdefault("_seen", set())]
            if not (row["user_id"] in _seen or _seen.add(row["user_id"]))
        }

        mapping = {}
        unresolved = []

        for employee in Employee.objects.all().order_by("id"):
            if not employee.user_id:
                unresolved.append(
                    {
                        "employee_id": employee.id,
                        "reason": "employee.user_id vacío",
                    }
                )
                continue

            candidates = users_by_user_id.get(employee.user_id, [])
            if not candidates:
                unresolved.append(
                    {
                        "employee_id": employee.id,
                        "employee_user_id": employee.user_id,
                        "reason": "sin candidate en users por user_id",
                    }
                )
                continue

            if len(candidates) == 1:
                selected = candidates[0]
            else:
                preferred_device = top_device_by_user_id.get(employee.user_id)
                if preferred_device is None:
                    unresolved.append(
                        {
                            "employee_id": employee.id,
                            "employee_user_id": employee.user_id,
                            "reason": "múltiples users para user_id y sin AttendanceLog para desambiguar device",
                            "candidate_user_ids": [c.id for c in candidates],
                        }
                    )
                    continue

                filtered = [c for c in candidates if c.device_id == preferred_device]
                if len(filtered) != 1:
                    unresolved.append(
                        {
                            "employee_id": employee.id,
                            "employee_user_id": employee.user_id,
                            "reason": "múltiples users para user_id incluso con device preferido",
                            "preferred_device_id": preferred_device,
                            "candidate_user_ids": [c.id for c in candidates],
                        }
                    )
                    continue

                selected = filtered[0]

            mapping[str(employee.id)] = {
                "employee_user_id": employee.user_id,
                "user_pk": selected.id,
                "user_device_id": selected.device_id,
                "user_uid": selected.uid,
            }

        self.stdout.write(self.style.NOTICE("=== RESOLVE Employee -> User ==="))
        self.stdout.write(f"Employees totales: {Employee.objects.count()}")
        self.stdout.write(f"Mappings resueltos: {len(mapping)}")
        self.stdout.write(f"No resueltos: {len(unresolved)}")

        if unresolved:
            self.stdout.write(self.style.WARNING("Muestras no resueltas:"))
            for row in unresolved[:10]:
                self.stdout.write(f" - {row}")

        if output:
            payload = {
                "resolved": mapping,
                "unresolved": unresolved,
            }
            with open(output, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
            self.stdout.write(self.style.SUCCESS(f"Mapping exportado en: {output}"))

        if unresolved:
            raise CommandError("Mapping incompleto: no es seguro eliminar Employee todavía.")

        self.stdout.write(self.style.SUCCESS("Mapping completo: listo para migración estructural."))
