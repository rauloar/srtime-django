"""
Create or update a ZKTeco terminal device in the database.
"""
from django.core.management.base import BaseCommand, CommandError
from core.models import Device


class Command(BaseCommand):
    help = "Create or update a ZKTeco terminal device"

    def add_arguments(self, parser):
        parser.add_argument(
            "--name",
            required=True,
            help="Device name",
        )
        parser.add_argument(
            "--ip",
            required=True,
            help="Device IP address",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=4370,
            help="Device port (default: 4370)",
        )
        parser.add_argument(
            "--enabled",
            action="store_true",
            default=True,
            help="Enable device",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing device if found",
        )

    def handle(self, *args, **options):
        name = options["name"]
        ip = options["ip"]
        port = options["port"]
        enabled = options["enabled"]
        update = options["update"]

        # Check if device exists
        existing = Device.objects.filter(ip=ip, port=port).first()

        if existing:
            if update:
                existing.name = name
                existing.enabled = enabled
                existing.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Device updated: {existing.name} ({existing.ip}:{existing.port})"
                    )
                )
                self.stdout.write(f"   ID: {existing.id}")
                self.stdout.write(f"   Enabled: {existing.enabled}")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  Device already exists: {existing.name} ({existing.ip}:{existing.port})"
                    )
                )
                self.stdout.write(f"   ID: {existing.id}")
                self.stdout.write(f"   Use --update to modify it")
        else:
            device = Device.objects.create(
                name=name,
                ip=ip,
                port=port,
                enabled=enabled,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Device created: {device.name} ({device.ip}:{device.port})"
                )
            )
            self.stdout.write(f"   ID: {device.id}")
            self.stdout.write(f"   Enabled: {device.enabled}")
