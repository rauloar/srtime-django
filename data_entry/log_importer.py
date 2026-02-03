"""
LOG Importer - Core Data Entry module.

Imports attendance LOG files from remote terminals (USB, flashdrives, etc.)
following the standard HR system workflow:

1. Company/Departments/Schedules are configured in the system
2. Employees are registered
3. Devices (terminals) are registered and enabled
4. Attendance data is imported from remote terminal LOGs

This module handles step 4: importing raw attendance events.

Output: Raw events without interpretation, validation, or persistence.

Usage:
    from data_entry.log_importer import import_attendance_log_by_device
    
    # Import LOG from a registered device
    events = import_attendance_log_by_device(
        log_file_path="fichajes.log",
        device_id=1  # Device registered in DB
    )
    print(f"Imported {len(events)} raw events")
"""

from typing import Any, Dict, List, Optional
from django.core.exceptions import ObjectDoesNotExist

from core.models import Device
from data_entry.file_adapter import FileAttendanceAdapter


def import_attendance_log_by_device(
    log_file_path: str,
    device_id: int,
) -> List[Dict[str, Any]]:
    """
    Import attendance events from a LOG file for a registered device.

    This is the primary method: receives a LOG file from a remote terminal
    and imports events for a device that's already configured in the system.

    Workflow:
    1. Device must exist and be enabled in the system
    2. LOG file contains raw attendance events
    3. Returns raw events for further processing (no persistence here)

    Args:
        log_file_path: Path to the .log file (e.g., "fichajes.log" from USB)
        device_id: Device ID (must exist in core.models.Device)

    Returns:
        List of raw event dictionaries (user_id, timestamp, status, punch, etc.)

    Raises:
        ObjectDoesNotExist: If device is not found or not enabled
        FileNotFoundError: If log file does not exist
        RuntimeError: If file parsing fails

    Example:
        # Device 5 is a terminal at the office entrance
        events = import_attendance_log_by_device(
            log_file_path="/mnt/usb/fichajes.log",
            device_id=5
        )
        print(f"Imported {len(events)} events for device {device_id}")
        for event in events:
            print(f"User {event['user_id']} @ {event['timestamp']}")
    """
    # Validate device exists and is enabled
    try:
        device = Device.objects.get(id=device_id, enabled=True)
    except Device.DoesNotExist:
        raise ObjectDoesNotExist(
            f"Device {device_id} not found or not enabled. "
            f"Please register the device in System Configuration."
        )

    # Import raw events from LOG file
    adapter = FileAttendanceAdapter(
        file_path=log_file_path,
        format_type="log",
        source_device_id=str(device_id),
    )
    events = adapter.read_attendance()

    return events


def import_attendance_log_generic(
    log_file_path: str,
    device_identifier: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Import attendance events from a LOG file (generic, no device validation).

    Use this only for offline/testing scenarios. For production, use
    `import_attendance_log_by_device()` instead.

    Args:
        log_file_path: Path to the .log file
        device_identifier: Optional device name/identifier

    Returns:
        List of raw event dictionaries

    Raises:
        FileNotFoundError: If log file does not exist
        RuntimeError: If file parsing fails
    """
    adapter = FileAttendanceAdapter(
        file_path=log_file_path,
        format_type="log",
        source_device_id=device_identifier,
    )
    return adapter.read_attendance()


def import_attendance_csv_by_device(
    csv_file_path: str,
    device_id: int,
) -> List[Dict[str, Any]]:
    """
    Import attendance events from a CSV file for a registered device.

    CSV format (no headers): user_id,timestamp,status,punch

    Args:
        csv_file_path: Path to the .csv file
        device_id: Device ID (must exist in core.models.Device)

    Returns:
        List of raw event dictionaries

    Raises:
        ObjectDoesNotExist: If device not found or not enabled
        FileNotFoundError: If file does not exist
        RuntimeError: If file parsing fails
    """
    # Validate device
    try:
        device = Device.objects.get(id=device_id, enabled=True)
    except Device.DoesNotExist:
        raise ObjectDoesNotExist(
            f"Device {device_id} not found or not enabled."
        )

    adapter = FileAttendanceAdapter(
        file_path=csv_file_path,
        format_type="csv",
        source_device_id=str(device_id),
    )
    return adapter.read_attendance()
