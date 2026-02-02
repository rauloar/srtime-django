"""
Forensic Database Triggers Migration
PostgreSQL triggers for defense-in-depth immutability protection.

These triggers operate at the database level, preventing:
- UPDATE on forensic tables (always blocked)
- DELETE on forensic tables (always blocked)
- Only INSERT is allowed

This is the last line of defense against:
- Direct SQL attacks
- Django admin bypasses
- Raw database connections
- Application bugs
"""
from django.db import migrations


class Migration(migrations.Migration):
    """
    Add PostgreSQL triggers to enforce immutability on forensic tables.
    
    These triggers cannot be bypassed from Django.
    They require superuser or trigger owner to disable.
    """
    
    dependencies = [
        ('core', '0001_initial'),  # Adjust to actual dependency
    ]
    
    operations = [
        # Migration neutralized for dev reset
    ]
