"""
Simulate a ZKTeco terminal sending attendance logs to the system.

This simulates real terminal behavior:
- Sends logs individually (not bulk)
- Respects signal processing
- Triggers validators and business logic
- Can replay data multiple times for stress testing
"""
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from core.models import AttendanceLog, Device, Employee


class Command(BaseCommand):
    help = "Simulate a ZKTeco terminal sending attendance logs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--device-id",
            type=int,
            required=True,
            help="Device ID to send logs from",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0,
            help="Delay in seconds between each log (default: 0 = no delay)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of logs to send (0 = all)",
        )
        parser.add_argument(
            "--start-offset",
            type=int,
            default=0,
            help="Start from Nth log (for resuming)",
        )
        parser.add_argument(
            "--repeat",
            type=int,
            default=1,
            help="Repeat simulation N times (good for stress testing)",
        )
        parser.add_argument(
            "--time-offset",
            type=int,
            default=0,
            help="Days to offset timestamps (useful for replay)",
        )
        parser.add_argument(
            "--batch-mode",
            action="store_true",
            help="Use bulk_create instead of individual creates (for baseline comparison)",
        )

    def handle(self, *args, **options):
        device_id = options["device_id"]
        delay = options["delay"]
        limit = options["limit"]
        start_offset = options["start_offset"]
        repeat_count = options["repeat"]
        time_offset = options["time_offset"]
        batch_mode = options["batch_mode"]

        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            raise CommandError(f"Device {device_id} not found")

        self.stdout.write(self.style.SUCCESS(f"\n=== ZKTeco Terminal Simulator ==="))
        self.stdout.write(f"Device: {device.name} ({device.ip}:{device.port})")
        self.stdout.write(f"Delay between logs: {delay}s")
        self.stdout.write(f"Time offset: {time_offset} days")
        self.stdout.write(f"Batch mode: {batch_mode}")
        self.stdout.write(f"Repeats: {repeat_count}\n")

        for repeat_idx in range(repeat_count):
            self.stdout.write(
                self.style.WARNING(f"\n--- Repeat {repeat_idx + 1}/{repeat_count} ---")
            )
            self._simulate_terminal(
                device=device,
                delay=delay,
                limit=limit,
                start_offset=start_offset,
                time_offset=time_offset,
                batch_mode=batch_mode,
                repeat_idx=repeat_idx,
            )

    def _simulate_terminal(
        self,
        device: Device,
        delay: float,
        limit: int,
        start_offset: int,
        time_offset: int,
        batch_mode: bool,
        repeat_idx: int,
    ) -> None:
        """Simulate terminal sending logs one by one"""
        
        # Get all existing logs (exclude the device import ones if you want)
        queryset = AttendanceLog.objects.all().order_by("timestamp")
        
        if limit > 0:
            queryset = queryset[:limit]
        
        total = queryset.count()
        sent = 0
        failed = 0
        start_time = time.time()

        if batch_mode:
            # Batch mode: use bulk_create for baseline comparison
            logs_to_create = []
            for idx, log in enumerate(queryset):
                if idx < start_offset:
                    continue
                
                # Create a new log with offset timestamp
                new_log = AttendanceLog(
                    device=device,
                    employee=log.employee,
                    user_id=log.user_id,
                    timestamp=log.timestamp + timedelta(days=time_offset + repeat_idx * 365),
                    status=log.status,
                    punch=log.punch,
                    verify_mode=log.verify_mode,
                    workstate=log.workstate,
                    workcode=log.workcode,
                    punch_source=log.punch_source,
                )
                logs_to_create.append(new_log)
            
            # Bulk create all
            if logs_to_create:
                AttendanceLog.objects.bulk_create(logs_to_create)
                self.stdout.write(f"Bulk created: {len(logs_to_create)} logs")
                sent = len(logs_to_create)
        else:
            # Terminal mode: individual creates (real behavior)
            for idx, log in enumerate(queryset):
                if idx < start_offset:
                    continue

                try:
                    # Simulate terminal sending this log
                    new_timestamp = log.timestamp + timedelta(
                        days=time_offset + repeat_idx * 365
                    )
                    
                    new_log = AttendanceLog.objects.create(
                        device=device,
                        employee=log.employee,
                        user_id=log.user_id,
                        timestamp=new_timestamp,
                        status=log.status,
                        punch=log.punch,
                        verify_mode=log.verify_mode,
                        workstate=log.workstate,
                        workcode=log.workcode,
                        punch_source=log.punch_source,
                    )
                    
                    sent += 1
                    
                    # Progress output every 100 logs
                    if sent % 100 == 0:
                        elapsed = time.time() - start_time
                        rate = sent / elapsed if elapsed > 0 else 0
                        self.stdout.write(
                            f"Sent {sent}/{total} logs ({rate:.1f} logs/sec)"
                        )
                    
                    # Apply delay if specified
                    if delay > 0:
                        time.sleep(delay)
                        
                except Exception as e:
                    failed += 1
                    if failed <= 5:  # Show first 5 errors
                        self.stdout.write(self.style.ERROR(f"Error on log {idx}: {e}"))

        elapsed = time.time() - start_time
        rate = sent / elapsed if elapsed > 0 else 0

        self.stdout.write(self.style.SUCCESS(f"\n=== Simulation Complete ==="))
        self.stdout.write(f"Logs sent: {sent}")
        self.stdout.write(f"Failed: {failed}")
        self.stdout.write(f"Time elapsed: {elapsed:.2f}s")
        self.stdout.write(f"Rate: {rate:.1f} logs/sec")
