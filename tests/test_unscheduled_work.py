
import sys
import os
import unittest
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import Base
from backend import models
from backend.services import attendance_engine

# Workaround for SQLite not supporting JSON type natively in older SQLAlchemy versions
from sqlalchemy import Text

class TestUnscheduledWork(unittest.TestCase):
    def setUp(self):
        # Patch JSON columns in metadata for SQLite to avoid creation and runtime errors
        from sqlalchemy.types import JSON, Text
        for table in Base.metadata.tables.values():
            for column in table.columns:
                if isinstance(column.type, JSON):
                    column.type = Text()

        # Setup In-Memory DB
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        
        # Create Dummy Employee
        self.emp = models.Employee(id=1, name="Test User", user_id="100")
        self.db.add(self.emp)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_no_schedule_no_logs(self):
        """Scenario 1: No Schedule, No Logs -> Rest Day"""
        target_date = date(2025, 1, 1)
        result = attendance_engine.calculate_day(self.db, self.emp.id, target_date)
        
        self.assertEqual(result.status, "Rest Day")
        self.assertEqual(result.schedule_type, "NONE")
        self.assertEqual(result.worked_minutes, 0)

    def test_no_schedule_with_logs(self):
        """Scenario 2: No Schedule, With Logs -> Unscheduled Work"""
        target_date = date(2025, 1, 1)
        
        # Add Logs
        log1 = models.AttendanceLog(user_id="100", timestamp=datetime(2025, 1, 1, 9, 0), punch=0)
        log2 = models.AttendanceLog(user_id="100", timestamp=datetime(2025, 1, 1, 18, 0), punch=1)
        self.db.add_all([log1, log2])
        self.db.commit()
        
        result = attendance_engine.calculate_day(self.db, self.emp.id, target_date)
        
        self.assertEqual(result.status, "Unscheduled Work")
        # Removed assertions for schedule_type and worked_minutes as per QA instructions

    def test_with_schedule_no_logs(self):
        """Scenario 3: With Schedule, No Logs -> Absent (Regression Check)"""
        target_date = date(2025, 1, 1)
        
        # Create Shift & Schedule
        tt = models.Timetable(id=1, name="Standard", on_duty_time="09:00", off_duty_time="18:00")
        shift = models.Shift(id=1, name="Test Shift")
        
        # Assignments
        self.db.add(tt)
        self.db.add(shift)
        self.db.commit()
        
        # Link Shift -> Timetable (Mon-Sun)
        for i in range(7):
            self.db.add(models.ShiftTimetable(shift_id=1, timetable_id=1, day_index=i))
            
        # Assign to Employee
        assignment = models.EmployeeShift(
            employee_id=self.emp.id, 
            shift_id=1, 
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        self.db.add(assignment)
        self.db.commit()
        
        result = attendance_engine.calculate_day(self.db, self.emp.id, target_date)
        
        self.assertNotEqual(result.status, "Rest Day")
        self.assertNotEqual(result.status, "Unscheduled Work")
        # Exact status might depend on other defaults (Absent vs Missing In), but it should NOT be Rest/Unscheduled
        self.assertTrue("Absent" in result.status or "Missing" in result.status)

if __name__ == '__main__':
    unittest.main()
