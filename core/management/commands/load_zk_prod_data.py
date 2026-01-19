"""
Management command to load zk_prod mock data into Django database.

Usage:
    python manage.py load_zk_prod_data [--schema] [--data]

Options:
    --schema    Load schema only (create tables)
    --data      Load data only (requires schema already loaded)
    --both      Load both schema and data (default)
"""
import sys
import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
import psycopg2
from psycopg2 import sql


class Command(BaseCommand):
    help = 'Load zk_prod mock data from exported SQL files into PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            action='store_true',
            help='Load schema only',
        )
        parser.add_argument(
            '--data',
            action='store_true',
            help='Load data only (requires schema already loaded)',
        )
        parser.add_argument(
            '--both',
            action='store_true',
            default=True,
            help='Load both schema and data (default)',
        )

    def handle(self, *args, **options):
        # Determine what to load
        load_schema = options['schema'] or options['both']
        load_data = options['data'] or options['both']

        # Get migration data directory
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        migration_dir = base_dir / 'migration_data'
        schema_file = migration_dir / 'zk_prod_schema.sql'
        data_file = migration_dir / 'zk_prod_data.sql'

        # Validate files exist
        if load_schema and not schema_file.exists():
            raise CommandError(f'Schema file not found: {schema_file}')
        if load_data and not data_file.exists():
            raise CommandError(f'Data file not found: {data_file}')

        try:
            # Get connection details from Django settings
            from django.conf import settings
            db_config = settings.DATABASES['default']

            if db_config['ENGINE'] != 'django.db.backends.postgresql':
                raise CommandError('This command only works with PostgreSQL databases.')

            # Connect directly to PostgreSQL
            conn = psycopg2.connect(
                dbname=db_config['NAME'],
                user=db_config['USER'],
                password=db_config['PASSWORD'],
                host=db_config['HOST'],
                port=db_config['PORT'],
            )
            cursor = conn.cursor()

            # Load schema
            if load_schema:
                self.stdout.write(self.style.SUCCESS('📋 Loading schema...'))
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                
                # Execute schema SQL (may need to split by statements)
                try:
                    cursor.execute(schema_sql)
                    conn.commit()
                    self.stdout.write(self.style.SUCCESS('  ✓ Schema loaded successfully'))
                except Exception as e:
                    conn.rollback()
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ Schema loading had issues: {str(e)[:100]}')
                    )

            # Load data
            if load_data:
                self.stdout.write(self.style.SUCCESS('📦 Loading data...'))
                with open(data_file, 'r', encoding='utf-8') as f:
                    data_sql = f.read()
                
                try:
                    cursor.execute(data_sql)
                    conn.commit()
                    self.stdout.write(self.style.SUCCESS('  ✓ Data loaded successfully'))
                except Exception as e:
                    conn.rollback()
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ Data loading had issues: {str(e)[:100]}')
                    )

            cursor.close()
            conn.close()

            # Verify counts
            self.stdout.write(self.style.SUCCESS('\n✅ Load process completed'))
            self.verify_counts()

        except Exception as e:
            raise CommandError(f'Error loading data: {str(e)}')

    def verify_counts(self):
        """Verify that data was loaded by checking row counts in key tables."""
        from core.models import (
            Company, Employee, Department, Device, AttendanceLog
        )

        self.stdout.write(self.style.SUCCESS('\n📊 Data Verification:'))
        
        counts = {
            'Companies': Company.objects.count(),
            'Employees': Employee.objects.count(),
            'Departments': Department.objects.count(),
            'Devices': Device.objects.count(),
            'Attendance Logs': AttendanceLog.objects.count(),
        }

        for model_name, count in counts.items():
            status = '✓' if count > 0 else '✗'
            self.stdout.write(f'  {status} {model_name}: {count}')
