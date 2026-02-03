"""Quick test of log_importer module."""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from data_entry.log_importer import import_attendance_log

log_file = "tests/data_entry/fixtures/attendance_small.log"
events = import_attendance_log(log_file, device_id="test_device_001")

print(f"\n✅ Imported {len(events)} events from {log_file}")
print(f"\nSample events (first 5):")
for i, event in enumerate(events[:5], 1):
    print(f"  {i}. User {event['user_id']:>3} @ {event['timestamp']} (punch={event['punch']}, status={event['status']})")

print(f"\nEvent structure: {list(events[0].keys()) if events else 'N/A'}")
print(f"Source: {events[0]['source'] if events else 'N/A'}")
print(f"Device ID: {events[0]['device_id'] if events else 'N/A'}")
print(f"\n✅ Test completed successfully!")
