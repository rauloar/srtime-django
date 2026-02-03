"""
Generate realistic attendance LOG files for testing.

Simulates a remote terminal that creates a .log file (e.g., via USB/flashdrive).
These logs are then imported by data_entry.log_importer module.

Usage:
    python tests/data_entry/generate_attendance_file.py
    
    Generates files like: tests/data_entry/fixtures/attendance_*.log
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
import random


def generate_attendance_log(
    output_dir: str = "tests/data_entry/fixtures",
    scenario: str = "medium",
) -> str:
    """
    Generate realistic attendance LOG file.
    
    Simulates output from a remote terminal device.
    
    Args:
        output_dir: Directory to write file
        scenario: 'small' (3 users, 1 device), 'medium' (100 users, 3 devices), 
                  'large' (1000 users, 4 devices)
    
    Returns:
        Path to generated .log file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if scenario == "small":
        events = _generate_small_scenario()
    elif scenario == "medium":
        events = _generate_medium_scenario()
    elif scenario == "large":
        events = _generate_large_scenario()
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    # Sort by timestamp
    events.sort(key=lambda e: e[1])

    log_path = output_path / f"attendance_{scenario}.log"

    # Write LOG file (format: user_id : timestamp (status, punch))
    with open(log_path, "w") as f:
        for user_id, timestamp, status, punch in events:
            f.write(f"{user_id} : {timestamp.strftime('%Y-%m-%d %H:%M:%S')} ({status}, {punch})\n")

    return str(log_path)


def _generate_small_scenario() -> List[Tuple[int, datetime, int, int]]:
    """3 employees, 1 device, 5 days."""
    events = []
    base_date = datetime(2026, 2, 1)
    user_ids = [100, 101, 102]
    device_id = 1

    for day_offset in range(5):
        day = base_date + timedelta(days=day_offset)

        for user_id in user_ids:
            # Random pattern: complete day, incomplete, or broken
            pattern = random.choice(["complete", "incomplete", "broken"])

            if pattern == "complete":
                # 09:00 IN, 12:00 OUT (break), 13:00 IN, 18:00 OUT
                events.append((user_id, day.replace(hour=9, minute=0), 0, 0))
                events.append((user_id, day.replace(hour=12, minute=0), 0, 1))
                events.append((user_id, day.replace(hour=13, minute=0), 1, 3))
                events.append((user_id, day.replace(hour=18, minute=0), 2, 1))

            elif pattern == "incomplete":
                # Only IN, no OUT
                events.append((user_id, day.replace(hour=9, minute=0), 0, 0))

            else:  # broken
                # Multiple entries or errors
                events.append((user_id, day.replace(hour=9, minute=5), 1, 0))
                events.append((user_id, day.replace(hour=9, minute=6), 1, 0))  # Duplicate
                events.append((user_id, day.replace(hour=18, minute=0), 2, 1))

    return events


def _generate_medium_scenario() -> List[Tuple[int, datetime, int, int]]:
    """100 employees, 3 devices, 10 days, stress-test level."""
    events = []
    base_date = datetime(2026, 1, 15)
    user_ids = list(range(1000, 1100))  # 100 users
    device_ids = [1, 2, 3]

    patterns_list = ["complete", "incomplete", "broken", "break_extended", "late"]
    punch_values = [0, 1, 2, 3]  # entrada, salida, salida_int, entrada_int
    status_values = [0, 1, 2, 3]  # face, fingerprint, pass, rfid

    for day_offset in range(10):
        day = base_date + timedelta(days=day_offset)

        for user_id in user_ids:
            pattern = random.choice(patterns_list)
            device_id = random.choice(device_ids)
            status = random.choice(status_values)

            if pattern == "complete":
                # Normal: 09:00 IN, 12:00 break, 13:00 back, 18:00 OUT
                events.append((user_id, day.replace(hour=9, minute=random.randint(0, 10)), status, 0))
                events.append((user_id, day.replace(hour=12, minute=random.randint(0, 10)), status, 1))
                events.append((user_id, day.replace(hour=13, minute=random.randint(0, 10)), status, 3))
                events.append((user_id, day.replace(hour=18, minute=random.randint(0, 10)), status, 1))

            elif pattern == "incomplete":
                # Only IN
                events.append((user_id, day.replace(hour=9, minute=random.randint(0, 10)), status, 0))

            elif pattern == "broken":
                # Multiple IN in a row (device error)
                events.append((user_id, day.replace(hour=9, minute=0), status, 0))
                events.append((user_id, day.replace(hour=9, minute=random.randint(1, 5)), status, 0))
                events.append((user_id, day.replace(hour=18, minute=0), status, 1))

            elif pattern == "break_extended":
                # Long break or multiple breaks
                events.append((user_id, day.replace(hour=9, minute=0), status, 0))
                events.append((user_id, day.replace(hour=11, minute=30), status, 1))
                events.append((user_id, day.replace(hour=13, minute=30), status, 3))
                events.append((user_id, day.replace(hour=14, minute=15), status, 1))
                events.append((user_id, day.replace(hour=15, minute=0), status, 3))
                events.append((user_id, day.replace(hour=18, minute=0), status, 1))

            else:  # late
                # Late arrival
                events.append((user_id, day.replace(hour=10, minute=random.randint(0, 30)), status, 0))
                events.append((user_id, day.replace(hour=18, minute=0), status, 1))

    return events


def _generate_large_scenario() -> List[Tuple[int, datetime, int, int]]:
    """1000 employees, 4 devices, 20 days, full stress-test."""
    events = []
    base_date = datetime(2025, 12, 1)
    user_ids = list(range(10000, 11000))  # 1000 users
    device_ids = [1, 2, 3, 4]

    patterns_list = ["complete", "incomplete", "broken", "break_extended", "late", "absent"]
    punch_values = [0, 1, 2, 3, 4, 5]  # All punch types
    status_values = [0, 1, 2, 3]

    for day_offset in range(20):
        day = base_date + timedelta(days=day_offset)
        
        # Skip weekends (basic)
        if day.weekday() >= 5:  # Saturday=5, Sunday=6
            continue

        for user_id in user_ids:
            # Vary pattern distribution for realism
            rand = random.random()
            if rand < 0.70:
                pattern = "complete"
            elif rand < 0.82:
                pattern = "incomplete"
            elif rand < 0.88:
                pattern = "broken"
            elif rand < 0.95:
                pattern = "break_extended"
            elif rand < 0.98:
                pattern = "late"
            else:
                pattern = "absent"

            device_id = random.choice(device_ids)
            status = random.choice(status_values)

            if pattern == "complete":
                events.append((user_id, day.replace(hour=9, minute=random.randint(0, 15)), status, 0))
                events.append((user_id, day.replace(hour=12, minute=random.randint(0, 15)), status, 1))
                events.append((user_id, day.replace(hour=13, minute=random.randint(0, 15)), status, 3))
                events.append((user_id, day.replace(hour=18, minute=random.randint(0, 15)), status, 1))

            elif pattern == "incomplete":
                events.append((user_id, day.replace(hour=9, minute=random.randint(0, 15)), status, 0))

            elif pattern == "broken":
                events.append((user_id, day.replace(hour=9, minute=0), status, 0))
                events.append((user_id, day.replace(hour=9, minute=random.randint(1, 3)), status, 0))
                events.append((user_id, day.replace(hour=18, minute=0), status, 1))

            elif pattern == "break_extended":
                events.append((user_id, day.replace(hour=9, minute=0), status, 0))
                events.append((user_id, day.replace(hour=11, minute=30), status, 1))
                events.append((user_id, day.replace(hour=13, minute=30), status, 3))
                events.append((user_id, day.replace(hour=14, minute=15), status, 1))
                events.append((user_id, day.replace(hour=15, minute=0), status, 3))
                events.append((user_id, day.replace(hour=18, minute=0), status, 1))

            elif pattern == "late":
                events.append((user_id, day.replace(hour=10, minute=random.randint(0, 45)), status, 0))
                events.append((user_id, day.replace(hour=18, minute=0), status, 1))

            # absent: no events for this user/day

    return events


if __name__ == "__main__":
    print("🔧 Generating attendance LOG files (simulating remote terminal output)...\n")

    print("Generating small scenario (3 employees, 1 device, 5 days)...")
    log_small = generate_attendance_log(scenario="small")
    print(f"  ✅ {log_small}")

    print("\nGenerating medium scenario (100 employees, 3 devices, 10 days)...")
    log_med = generate_attendance_log(scenario="medium")
    print(f"  ✅ {log_med}")

    print("\nGenerating large scenario (1000 employees, 4 devices, 20 days)...")
    log_large = generate_attendance_log(scenario="large")
    print(f"  ✅ {log_large}")

    print("\n" + "=" * 80)
    print("✅ LOG files generated successfully!")
    print("=" * 80)
    print("\nThese files simulate logs from a remote terminal (e.g., USB/flashdrive).")
    print("Import them using: data_entry.log_importer.import_attendance_log()")
    print("\nExample:")
    print(f"  from data_entry.log_importer import import_attendance_log")
    print(f"  events = import_attendance_log('{log_small}')")
