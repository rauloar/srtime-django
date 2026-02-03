"""
CSV Export Script - Production-like Report from Dev Seeds
Exports AttendanceLog data to CSV format simulating production export.
No hardcoding - reads directly from database.

Usage:
    python manage.py shell -c "from tests.export_seeds_csv import export_attendance_csv; export_attendance_csv()"
"""

import csv
import os
from core.models import AttendanceLog

def export_attendance_csv(output_dir='AUDITORIAS'):
    """
    Export AttendanceLog records to CSV format.
    
    Aggregates logs per user_id/date pair and calculates:
    - First check-in (IN event, punch=0)
    - Last check-out (OUT event, punch=1)
    - Duration in minutes
    - Status (Normal/Incomplete/Error)
    
    Args:
        output_dir (str): Directory to save CSV file
    
    Returns:
        str: Path to generated CSV file
    """
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    csv_filename = os.path.join(output_dir, 'seeds_production_report.csv')
    
    # Query all attendance logs ordered by timestamp
    logs = AttendanceLog.objects.order_by('timestamp').all()
    
    if not logs.exists():
        print(f"Warning: No attendance logs found in database")
        return csv_filename
    
    # Group logs by user_id and date
    aggregated = {}
    for log in logs:
        log_date = log.timestamp.date()
        key = (log_date, log.user_id)
        if key not in aggregated:
            aggregated[key] = {
                'date': log_date,
                'user_id': log.user_id,
                'events': []
            }
        aggregated[key]['events'].append(log)
    
    # Write CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'date',
            'user_id',
            'check_in_time',
            'check_out_time',
            'duration_minutes',
            'event_count',
            'status',
            'raw_events'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write aggregated data
        for (date, user_id), data in sorted(aggregated.items()):
            events = data['events']
            
            # Extract check-in and check-out (punch: 0=IN, 1=OUT)
            in_events = [e for e in events if e.punch == 0]
            out_events = [e for e in events if e.punch == 1]
            
            check_in_time = in_events[0].timestamp.strftime('%H:%M:%S') if in_events else 'N/A'
            check_out_time = out_events[-1].timestamp.strftime('%H:%M:%S') if out_events else 'N/A'
            
            # Calculate duration
            if in_events and out_events:
                duration = int((out_events[-1].timestamp - in_events[0].timestamp).total_seconds() / 60)
                status = 'Normal'
            elif in_events and not out_events:
                duration = 0
                status = 'Incomplete'
            else:
                duration = 0
                status = 'Error'
            
            # Raw events for debugging
            punch_labels = {0: 'IN', 1: 'OUT'}
            raw_events = ' | '.join([
                f"{e.timestamp.strftime('%H:%M:%S')}-{punch_labels.get(e.punch, str(e.punch))}" 
                for e in events
            ])
            
            writer.writerow({
                'date': date.strftime('%Y-%m-%d'),
                'user_id': user_id,
                'check_in_time': check_in_time,
                'check_out_time': check_out_time,
                'duration_minutes': duration,
                'event_count': len(events),
                'status': status,
                'raw_events': raw_events
            })
    
    print(f"CSV exported to: {csv_filename}")
    print(f"Total records: {len(aggregated)}")
    
    # Print summary
    print("\nSummary:")
    print(f"{'Date':<12} {'User ID':<12} {'Check-In':<12} {'Check-Out':<12} {'Duration':<10} {'Status':<12}")
    print("-" * 80)
    
    for (date, user_id), data in sorted(aggregated.items()):
        events = data['events']
        in_events = [e for e in events if e.punch == 0]
        out_events = [e for e in events if e.punch == 1]
        
        check_in = in_events[0].timestamp.strftime('%H:%M:%S') if in_events else 'N/A'
        check_out = out_events[-1].timestamp.strftime('%H:%M:%S') if out_events else 'N/A'
        
        if in_events and out_events:
            duration = int((out_events[-1].timestamp - in_events[0].timestamp).total_seconds() / 60)
            status = 'Normal'
        elif in_events and not out_events:
            duration = 0
            status = 'Incomplete'
        else:
            duration = 0
            status = 'Error'
        
        print(f"{date} {user_id:<12} {check_in:<12} {check_out:<12} {duration:<10}min {status:<12}")
    
    return csv_filename


if __name__ == '__main__':
    export_attendance_csv()
