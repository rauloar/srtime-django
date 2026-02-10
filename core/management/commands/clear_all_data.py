"""
Management command to clear all data from the database.
More explicit and safer than Django's flush command.
"""
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import (
    AttendanceLog, ScheduleOverride, EmployeeShift, Employee,
    ShiftTimetable, Shift, Timetable, Department, Company, Device
)

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Clear all data from the database (keeps table structure)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n⚠️  DATABASE CLEAR OPERATION'))
        self.stdout.write('=' * 70)
        
        # Show current data counts
        counts = self.get_data_counts()
        self.stdout.write('\n📊 Current database status:')
        for model_name, count in counts.items():
            if count > 0:
                self.stdout.write(f'  • {model_name}: {count}')
        
        total_records = sum(counts.values())
        
        if total_records == 0:
            self.stdout.write(self.style.SUCCESS('\n✅ Database is already empty!'))
            return
        
        self.stdout.write(f'\n🗑️  Total records to delete: {total_records}')
        
        # Confirmation prompt
        if not options['no_input']:
            self.stdout.write(self.style.WARNING('\n⚠️  This action cannot be undone!'))
            confirm = input('\nType "DELETE ALL" to confirm: ')
            if confirm != 'DELETE ALL':
                self.stdout.write(self.style.ERROR('\n❌ Operation cancelled.'))
                return
        
        # Execute deletion
        self.stdout.write('\n🔄 Clearing database...')
        try:
            deleted_counts = self.clear_all_data()
            
            # Verify deletion
            remaining_counts = self.get_data_counts()
            total_remaining = sum(remaining_counts.values())
            
            if total_remaining == 0:
                self.stdout.write(self.style.SUCCESS('\n✅ Database cleared successfully!'))
                self.stdout.write('\n📋 Records deleted:')
                for model_name, count in deleted_counts.items():
                    if count > 0:
                        self.stdout.write(f'  • {model_name}: {count}')
                
                logger.info(f"Database cleared: {sum(deleted_counts.values())} records deleted")
            else:
                self.stdout.write(self.style.ERROR(f'\n⚠️  Warning: {total_remaining} records remain'))
                for model_name, count in remaining_counts.items():
                    if count > 0:
                        self.stdout.write(f'  • {model_name}: {count}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error during deletion: {e}'))
            logger.error(f"Database clear failed: {e}", exc_info=True)
            raise

    def get_data_counts(self):
        """Get count of records for each model."""
        return {
            'AttendanceLogs': AttendanceLog.objects.count(),
            'ScheduleOverrides': ScheduleOverride.objects.count(),
            'EmployeeShifts': EmployeeShift.objects.count(),
            'Employees': Employee.objects.count(),
            'ShiftTimetables': ShiftTimetable.objects.count(),
            'Shifts': Shift.objects.count(),
            'Timetables': Timetable.objects.count(),
            'Departments': Department.objects.count(),
            'Devices': Device.objects.count(),
            'Companies': Company.objects.count(),
        }

    def clear_all_data(self):
        """Delete all data in correct order (respecting foreign keys)."""
        deleted_counts = {}
        
        with transaction.atomic():
            # Delete in reverse dependency order
            deleted_counts['AttendanceLogs'] = AttendanceLog.objects.all().delete()[0]
            deleted_counts['ScheduleOverrides'] = ScheduleOverride.objects.all().delete()[0]
            deleted_counts['EmployeeShifts'] = EmployeeShift.objects.all().delete()[0]
            deleted_counts['Employees'] = Employee.objects.all().delete()[0]
            deleted_counts['ShiftTimetables'] = ShiftTimetable.objects.all().delete()[0]
            deleted_counts['Shifts'] = Shift.objects.all().delete()[0]
            deleted_counts['Timetables'] = Timetable.objects.all().delete()[0]
            deleted_counts['Departments'] = Department.objects.all().delete()[0]
            deleted_counts['Devices'] = Device.objects.all().delete()[0]
            deleted_counts['Companies'] = Company.objects.all().delete()[0]
        
        return deleted_counts
