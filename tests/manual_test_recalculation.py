
import sys
import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.getcwd())

from backend.database import settings
from backend import models
from backend.services.attendance_engine import calculate_day, resolve_schedule

def test_recalculation():
    print(f"Connecting to: {settings.DB_URL}")
    engine = create_engine(settings.DB_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Setup: Get a Department and an Employee in it
        dept = db.query(models.Department).first()
        if not dept:
            print("No department found.")
            return

        emp = db.query(models.Employee).filter(models.Employee.department_id == dept.id).first()
        if not emp:
            # Try to assign one
            emp = db.query(models.Employee).first()
            if emp:
                emp.department_id = dept.id
                db.commit()
                print(f"Assigned Emp {emp.name} to Dept {dept.name}")
            else:
                print("No employees found.")
                return

        print(f"Testing with Emp: {emp.name} (Dept: {dept.name})")
        target_date = date(2025, 12, 15)
        
        # 2. Assign Shift to DEPARTMENT
        # Get a shift
        shift = db.query(models.Shift).first()
        if not shift:
            print("No shifts found.")
            return
            
        print(f"Assigning Shift {shift.name} to Department {dept.name}")
        
        # Clear existing assignments for this date/scope
        db.query(models.EmployeeShift).filter(
            models.EmployeeShift.department_id == dept.id,
            models.EmployeeShift.scope == 'DEPARTMENT'
        ).delete()
        
        dept_assign = models.EmployeeShift(
            department_id=dept.id,
            shift_id=shift.id,
            start_date=target_date,
            end_date=target_date,
            scope="DEPARTMENT"
        )
        db.add(dept_assign)
        db.commit()
        
        print(f"Emp ID: {emp.id}, Emp Dept ID: {emp.department_id}")
        
        # Verify assignment in DB
        chk = db.query(models.EmployeeShift).filter(models.EmployeeShift.department_id == dept.id).all()
        print(f"Found {len(chk)} department assignments.")
        for c in chk:
            print(f" - ID: {c.id}, Shift: {c.shift_id}, Start: {c.start_date}, End: {c.end_date}")
            
        # Verify Shift Cycle
        s_tt = db.query(models.ShiftTimetable).filter(models.ShiftTimetable.shift_id == shift.id).all()
        print(f"Shift Cycle items: {len(s_tt)}")
        day_idx = target_date.weekday()
        print(f"Target Day Index: {day_idx}")
        matching_tt = [s for s in s_tt if s.day_index == day_idx]
        if not matching_tt:
             print("WARNING: No timetable for this day index!")
        else:
             print(f"Timetable for day: {matching_tt[0].timetable_id}")

        # 3. Calculate and Verify (Should pick up Dept Shift)
        # Clear daily first
        db.query(models.DailyAttendance).filter(models.DailyAttendance.employee_id == emp.id, models.DailyAttendance.date == target_date).delete()
        db.commit()
        
        print("Calling resolve_schedule...")
        ctx = resolve_schedule(db, emp.id, target_date)
        if ctx:
             print(f"Context Source: {ctx.source}")
             if ctx.source == "DEPARTMENT":
                 print("PASS: Department Assignment used.")
             else:
                 print(f"FAIL: Source is {ctx.source}")
        else:
             print("FAIL: resolve_schedule returned None")

        # 4. Modify Assignment (Change Shift)
        # Find another shift
        # Find another shift
        other_shift = db.query(models.Shift).filter(models.Shift.id != shift.id).first()
        if other_shift:
            print(f"Modifying Dept Assignment to Shift {other_shift.name}")
            dept_assign.shift_id = other_shift.id
            db.commit()
            
            # 5. Recalculate
            res2 = calculate_day(db, emp.id, target_date)
            ctx2 = resolve_schedule(db, emp.id, target_date)
            
            print(f"Run 2 Timetable: {ctx2.timetable.name}")
            if ctx2.timetable.id != ctx.timetable.id: # Assuming shifts imply different timetables for same day
                 print("PASS: Recalculation updated timetable.")
            else:
                 print("WARN: Timetables are same, check if shifts point to different timetables.")

        # Cleanup
        db.delete(dept_assign)
        db.commit()

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_recalculation()
