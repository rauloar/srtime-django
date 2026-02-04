"""
Seed Django database from a ZKTimeNet SQL dump (text parsing only).

Rules:
- No SQL execution
- No schema changes
- Maps ZKTimeNet tables to existing Django models:
  hr_company → Company
  hr_department → Department
  att_zone → Zone
  att_timetable → Timetable
  att_shift → Shift
  hr_employee → Employee
  att_punches → AttendanceLog
  att_employee_shift → EmployeeShift
"""
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date

from core.models import (
    Company, Department, Zone, Timetable, Shift, Position,
    Employee, AttendanceLog, Device, EmployeeShift
)


class Command(BaseCommand):
    help = "Seed Django models from ZKTimeNet SQL dump (text parsing, no SQL execution)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sql-path",
            default=str(Path("caso_real_sql") / "ZKTimeNet.db.sql"),
            help="Path to ZKTimeNet SQL dump",
        )
        parser.add_argument(
            "--skip-companies",
            action="store_true",
            help="Skip Company creation",
        )
        parser.add_argument(
            "--skip-departments",
            action="store_true",
            help="Skip Department creation",
        )
        parser.add_argument(
            "--skip-zones",
            action="store_true",
            help="Skip Zone creation",
        )
        parser.add_argument(
            "--skip-timetables",
            action="store_true",
            help="Skip Timetable creation",
        )
        parser.add_argument(
            "--skip-shifts",
            action="store_true",
            help="Skip Shift creation",
        )
        parser.add_argument(
            "--skip-employees",
            action="store_true",
            help="Skip Employee creation",
        )
        parser.add_argument(
            "--skip-logs",
            action="store_true",
            help="Skip AttendanceLog creation",
        )
        parser.add_argument(
            "--skip-employee-shifts",
            action="store_true",
            help="Skip EmployeeShift creation",
        )
        parser.add_argument(
            "--limit-employees",
            type=int,
            default=0,
            help="Limit number of employees to import (0 = no limit)",
        )
        parser.add_argument(
            "--limit-logs",
            type=int,
            default=0,
            help="Limit number of logs to import (0 = no limit)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=5000,
            help="Batch size for bulk_create",
        )
        parser.add_argument(
            "--device-name",
            default="ZKTimeNet Import",
            help="Device name used for imported logs",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse data without writing to DB",
        )
        parser.add_argument(
            "--clear-all",
            action="store_true",
            help="Delete ALL imported records before import",
        )

    def handle(self, *args, **options):
        sql_path = Path(options["sql_path"]).resolve()
        if not sql_path.exists():
            raise CommandError(f"SQL file not found: {sql_path}")

        dry_run = options["dry_run"]
        clear_all = options["clear_all"]

        if clear_all and not dry_run:
            self.stdout.write(self.style.WARNING("Clearing all imported data..."))
            AttendanceLog.objects.all().delete()
            EmployeeShift.objects.all().delete()
            Employee.objects.all().delete()
            Shift.objects.all().delete()
            Timetable.objects.all().delete()
            Zone.objects.all().delete()
            Department.objects.all().delete()
            Company.objects.all().delete()

        device = self._get_import_device(options["device_name"], dry_run)

        self.stdout.write(self.style.SUCCESS("\n=== ZKTimeNet SQL Seed ==="))
        self.stdout.write(f"SQL file: {sql_path}")
        self.stdout.write(f"Dry-run: {dry_run}\n")

        # Dependency order: Company → Department → Zone → Timetable → Shift → Employee → EmployeeShift → AttendanceLog

        company_id_map: Dict[int, int] = {}
        if not options["skip_companies"]:
            self.stdout.write(self.style.SUCCESS("[1/8] Importing companies..."))
            company_id_map = self._import_companies(sql_path, dry_run)
        else:
            self.stdout.write(self.style.WARNING("[1/8] Companies import skipped."))

        dept_id_map: Dict[int, int] = {}
        if not options["skip_departments"]:
            self.stdout.write(self.style.SUCCESS("[2/8] Importing departments..."))
            dept_id_map = self._import_departments(sql_path, company_id_map, dry_run)
        else:
            self.stdout.write(self.style.WARNING("[2/8] Departments import skipped."))

        if not options["skip_zones"]:
            self.stdout.write(self.style.SUCCESS("[3/8] Importing zones..."))
            self._import_zones(sql_path, dry_run)
        else:
            self.stdout.write(self.style.WARNING("[3/8] Zones import skipped."))

        if not options["skip_timetables"]:
            self.stdout.write(self.style.SUCCESS("[4/8] Importing timetables..."))
            self._import_timetables(sql_path, dry_run)
        else:
            self.stdout.write(self.style.WARNING("[4/8] Timetables import skipped."))

        shift_id_map: Dict[int, int] = {}
        if not options["skip_shifts"]:
            self.stdout.write(self.style.SUCCESS("[5/8] Importing shifts..."))
            shift_id_map = self._import_shifts(sql_path, dry_run)
        else:
            self.stdout.write(self.style.WARNING("[5/8] Shifts import skipped."))

        employee_id_map: Dict[int, str] = {}
        if not options["skip_employees"]:
            self.stdout.write(self.style.SUCCESS("[6/8] Importing employees..."))
            employee_id_map = self._import_employees(
                sql_path, dept_id_map, limit=options["limit_employees"], dry_run=dry_run
            )
        else:
            self.stdout.write(self.style.WARNING("[6/8] Employees import skipped."))
            if not options["skip_logs"] or not options["skip_employee_shifts"]:
                employee_id_map = self._build_employee_id_map(sql_path)

        if not options["skip_employee_shifts"]:
            self.stdout.write(self.style.SUCCESS("[7/8] Importing employee shifts..."))
            self._import_employee_shifts(sql_path, employee_id_map, shift_id_map, dry_run)
        else:
            self.stdout.write(self.style.WARNING("[7/8] Employee shifts import skipped."))

        if not options["skip_logs"]:
            self.stdout.write(self.style.SUCCESS("[8/8] Importing attendance logs..."))
            self._import_logs(
                sql_path,
                employee_id_map=employee_id_map,
                device=device,
                limit=options["limit_logs"],
                batch_size=options["batch_size"],
                dry_run=dry_run,
            )
        else:
            self.stdout.write(self.style.WARNING("[8/8] Logs import skipped."))

        self.stdout.write(self.style.SUCCESS("\n=== Import Summary ==="))
        self.stdout.write(f"Companies: {Company.objects.count()}")
        self.stdout.write(f"Departments: {Department.objects.count()}")
        self.stdout.write(f"Zones: {Zone.objects.count()}")
        self.stdout.write(f"Timetables: {Timetable.objects.count()}")
        self.stdout.write(f"Shifts: {Shift.objects.count()}")
        self.stdout.write(f"Employees: {Employee.objects.count()}")
        self.stdout.write(f"EmployeeShifts: {EmployeeShift.objects.count()}")
        self.stdout.write(f"AttendanceLogs: {AttendanceLog.objects.count()}")

    def _get_import_device(self, device_name: str, dry_run: bool) -> Device:
        if dry_run:
            return Device(name=device_name, ip="0.0.0.0", port=4370, enabled=True)
        device, _ = Device.objects.get_or_create(
            name=device_name,
            defaults={
                "ip": "0.0.0.0",
                "port": 4370,
                "enabled": True,
            },
        )
        return device

    def _import_companies(self, sql_path: Path, dry_run: bool) -> Dict[int, int]:
        """
        Import companies from hr_company.
        Maps ZKTimeNet company id → Django Company id
        """
        count = 0
        id_map: Dict[int, int] = {}

        for columns, values in iter_insert_rows(sql_path, "hr_company"):
            row = dict(zip(columns, values))
            zk_id = to_int(row.get("id"))
            name = safe_str(row.get("company_name"))
            if not name:
                continue

            if not dry_run:
                company, _ = Company.objects.get_or_create(
                    name=name,
                    defaults={
                        "code": safe_str(row.get("company_code")) or None,
                        "address": safe_str(row.get("company_address")) or None,
                    },
                )
                if zk_id is not None:
                    id_map[zk_id] = company.id

            count += 1

        self.stdout.write(f"Companies parsed: {count}")
        return id_map

    def _import_departments(self, sql_path: Path, company_id_map: Dict[int, int], dry_run: bool) -> Dict[int, int]:
        """
        Import departments from hr_department.
        Maps ZKTimeNet department id → Django Department id
        """
        count = 0
        id_map: Dict[int, int] = {}

        for columns, values in iter_insert_rows(sql_path, "hr_department"):
            row = dict(zip(columns, values))
            zk_id = to_int(row.get("id"))
            name = safe_str(row.get("department_name"))
            if not name:
                continue

            zk_company_id = to_int(row.get("company_id"))
            company_id = company_id_map.get(zk_company_id) if zk_company_id else None

            if not dry_run:
                company_obj = Company.objects.get(id=company_id) if company_id else None
                dept, _ = Department.objects.get_or_create(
                    name=name,
                    defaults={
                        "code": safe_str(row.get("departement_code")) or None,
                        "company": company_obj,
                    },
                )
                if zk_id is not None:
                    id_map[zk_id] = dept.id

            count += 1

        self.stdout.write(f"Departments parsed: {count}")
        return id_map

    def _import_zones(self, sql_path: Path, dry_run: bool) -> Dict[int, int]:
        """
        Import zones from att_zone.
        Maps ZKTimeNet zone id → Django Zone id
        """
        count = 0
        id_map: Dict[int, int] = {}

        for columns, values in iter_insert_rows(sql_path, "att_zone"):
            row = dict(zip(columns, values))
            zk_id = to_int(row.get("id"))
            name = safe_str(row.get("zone_name"))
            if not name:
                continue

            if not dry_run:
                zone, _ = Zone.objects.get_or_create(
                    name=name,
                    defaults={
                        "code": safe_str(row.get("zone_code")) or None,
                    },
                )
                if zk_id is not None:
                    id_map[zk_id] = zone.id

            count += 1

        self.stdout.write(f"Zones parsed: {count}")
        return id_map

    def _import_timetables(self, sql_path: Path, dry_run: bool) -> Dict[int, int]:
        """
        Import timetables from att_timetable.
        Maps ZKTimeNet timetable id → Django Timetable id
        """
        count = 0
        id_map: Dict[int, int] = {}

        for columns, values in iter_insert_rows(sql_path, "att_timetable"):
            row = dict(zip(columns, values))
            zk_id = to_int(row.get("id"))
            name = safe_str(row.get("time_name"))
            if not name:
                continue

            # Extract time fields (Mon_In, Mon_Out, Tue_In, etc.)
            on_duty = safe_str(row.get("Mon_In")) or "09:00"
            off_duty = safe_str(row.get("Mon_Out")) or "18:00"

            if not dry_run:
                timetable, _ = Timetable.objects.get_or_create(
                    name=name,
                    defaults={
                        "on_duty_time": on_duty,
                        "off_duty_time": off_duty,
                        "late_allow_minutes": to_int(row.get("late_allow_minutes")) or 0,
                        "early_leave_allow_minutes": to_int(row.get("early_leave_allow_minutes")) or 0,
                        "break_minutes": to_int(row.get("break_minutes")) or 0,
                        "required_minutes": to_int(row.get("required_minutes")) or 0,
                    },
                )
                if zk_id is not None:
                    id_map[zk_id] = timetable.id

            count += 1

        self.stdout.write(f"Timetables parsed: {count}")
        return id_map

    def _import_shifts(self, sql_path: Path, dry_run: bool) -> Dict[int, int]:
        """
        Import shifts from att_shift.
        Maps ZKTimeNet shift id → Django Shift id
        """
        count = 0
        id_map: Dict[int, int] = {}

        for columns, values in iter_insert_rows(sql_path, "att_shift"):
            row = dict(zip(columns, values))
            zk_id = to_int(row.get("id"))
            name = safe_str(row.get("shift_name"))
            if not name:
                continue

            if not dry_run:
                shift, _ = Shift.objects.get_or_create(
                    name=name,
                )
                if zk_id is not None:
                    id_map[zk_id] = shift.id

            count += 1

        self.stdout.write(f"Shifts parsed: {count}")
        return id_map

    def _import_employees(self, sql_path: Path, dept_id_map: Dict[int, int], limit: int, dry_run: bool) -> Dict[int, str]:
        count = 0
        id_map: Dict[int, str] = {}

        for columns, values in iter_insert_rows(sql_path, "hr_employee"):
            row = dict(zip(columns, values))

            emp_id = to_int(row.get("id"))
            emp_pin = safe_str(row.get("emp_pin"))
            emp_pin2 = safe_str(row.get("emp_pin2"))
            emp_username = safe_str(row.get("emp_username"))
            user_id = emp_pin or emp_pin2 or emp_username or (str(emp_id) if emp_id is not None else "")
            if not user_id:
                continue

            first = safe_str(row.get("emp_firstname"))
            last = safe_str(row.get("emp_lastname"))
            name = " ".join([p for p in [first, last] if p]).strip() or None

            hire_date = parse_date_safe(row.get("emp_hiredate"))
            active = bool(to_int(row.get("emp_active")) or 0)

            # Link to department via dept_id_map
            zk_dept_id = to_int(row.get("department_id"))
            department_id = dept_id_map.get(zk_dept_id) if zk_dept_id else None

            if not dry_run:
                department_obj = Department.objects.get(id=department_id) if department_id else None
                Employee.objects.update_or_create(
                    user_id=user_id,
                    defaults={
                        "name": name,
                        "department": department_obj,
                        "phone": safe_str(row.get("emp_phone")) or None,
                        "email": safe_str(row.get("emp_email")) or None,
                        "hire_date": hire_date,
                        "address": safe_str(row.get("emp_address")) or None,
                        "city": safe_str(row.get("emp_city")) or None,
                        "country": safe_str(row.get("emp_country")) or None,
                        "ssn": safe_str(row.get("emp_ssn")) or None,
                        "active": active,
                    },
                )

            if emp_id is not None:
                id_map[emp_id] = user_id

            count += 1
            if limit and count >= limit:
                break

        self.stdout.write(f"Employees parsed: {count}")
        return id_map

    def _build_employee_id_map(self, sql_path: Path) -> Dict[int, str]:
        id_map: Dict[int, str] = {}
        for columns, values in iter_insert_rows(sql_path, "hr_employee"):
            row = dict(zip(columns, values))
            emp_id = to_int(row.get("id"))
            emp_pin = safe_str(row.get("emp_pin"))
            emp_pin2 = safe_str(row.get("emp_pin2"))
            emp_username = safe_str(row.get("emp_username"))
            user_id = emp_pin or emp_pin2 or emp_username or (str(emp_id) if emp_id is not None else "")
            if emp_id is not None and user_id:
                id_map[emp_id] = user_id
        return id_map

    def _import_employee_shifts(
        self,
        sql_path: Path,
        employee_id_map: Dict[int, str],
        shift_id_map: Dict[int, int],
        dry_run: bool,
    ) -> None:
        """
        Import employee shift assignments from att_employee_shift.
        Links Employee (by user_id) to Shift.
        """
        count = 0
        skipped = 0

        for columns, values in iter_insert_rows(sql_path, "att_employee_shift"):
            row = dict(zip(columns, values))

            emp_zk_id = to_int(row.get("emp_id"))
            user_id = employee_id_map.get(emp_zk_id)
            if not user_id:
                skipped += 1
                continue

            shift_zk_id = to_int(row.get("shift_id"))
            shift_id = shift_id_map.get(shift_zk_id)
            if not shift_id:
                skipped += 1
                continue

            start_date = parse_date_safe(row.get("start_date"))
            if not start_date:
                skipped += 1
                continue

            if not dry_run:
                try:
                    employee = Employee.objects.get(user_id=user_id)
                    shift = Shift.objects.get(id=shift_id)
                    
                    EmployeeShift.objects.get_or_create(
                        employee=employee,
                        shift=shift,
                        start_date=start_date,
                        defaults={
                            "scope": "EMPLOYEE",
                            "end_date": parse_date_safe(row.get("end_date")),
                        },
                    )
                except (Employee.DoesNotExist, Shift.DoesNotExist):
                    skipped += 1
                    continue

            count += 1

        self.stdout.write(f"EmployeeShifts parsed: {count}")
        if skipped:
            self.stdout.write(f"EmployeeShifts skipped: {skipped}")

    def _import_logs(
        self,
        sql_path: Path,
        employee_id_map: Dict[int, str],
        device: Device,
        limit: int,
        batch_size: int,
        dry_run: bool,
    ) -> None:
        count = 0
        missing_employee = 0
        batch: List[AttendanceLog] = []

        for columns, values in iter_insert_rows(sql_path, "att_punches"):
            row = dict(zip(columns, values))

            emp_id = to_int(row.get("employee_id"))
            user_id = employee_id_map.get(emp_id)
            if not user_id:
                missing_employee += 1
                continue

            timestamp = parse_datetime_safe(row.get("punch_time"))
            if timestamp is None:
                continue

            status = to_int(row.get("status")) or 0
            punch = to_int(row.get("punch_type")) or 0

            log = AttendanceLog(
                device=device,
                user_id=user_id,
                timestamp=timestamp,
                status=status,
                punch=punch,
                verify_mode=to_int(row.get("verifycode")),
                workstate=to_int(row.get("workstate")),
                workcode=to_int(row.get("workcode")),
                punch_source=safe_str(row.get("terminal_id")) or None,
                raw_json={
                    "employee_id": emp_id,
                    "terminal_id": row.get("terminal_id"),
                    "operator": row.get("operator"),
                    "operator_reason": row.get("operator_reason"),
                    "operator_time": row.get("operator_time"),
                    "attendance_event": row.get("attendance_event"),
                    "login_combination": row.get("login_combination"),
                    "annotation": row.get("annotation"),
                    "processed": row.get("processed"),
                    "middleware_id": row.get("middleware_id"),
                },
            )

            if not dry_run:
                batch.append(log)
                if len(batch) >= batch_size:
                    AttendanceLog.objects.bulk_create(batch, ignore_conflicts=True)
                    batch = []

            count += 1
            if limit and count >= limit:
                break

        if not dry_run and batch:
            AttendanceLog.objects.bulk_create(batch, ignore_conflicts=True)

        self.stdout.write(f"Logs parsed: {count}")
        self.stdout.write(f"Logs skipped (missing employee): {missing_employee}")


def iter_insert_rows(sql_path: Path, table_name: str) -> Iterable[Tuple[List[str], List[object]]]:
    prefix = f'INSERT INTO "{table_name}"'
    buffer = ""

    with sql_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if buffer:
                buffer += line
                if ";" in line:
                    yield from parse_insert_statement(buffer, table_name)
                    buffer = ""
                continue

            if line.startswith(prefix):
                if ";" in line:
                    yield from parse_insert_statement(line, table_name)
                else:
                    buffer = line

    if buffer:
        yield from parse_insert_statement(buffer, table_name)


def parse_insert_statement(statement: str, table_name: str) -> Iterable[Tuple[List[str], List[object]]]:
    pattern = rf'INSERT INTO "{re.escape(table_name)}" \((?P<cols>.+?)\) VALUES (?P<values>.+);'
    match = re.search(pattern, statement, flags=re.DOTALL)
    if not match:
        return []

    columns = re.findall(r'"([^"]+)"', match.group("cols"))
    values_section = match.group("values").strip()

    rows = []
    for group in split_value_groups(values_section):
        values = parse_sql_values(group)
        rows.append((columns, values))
    return rows


def split_value_groups(values_section: str) -> Iterable[str]:
    groups = []
    depth = 0
    start = None
    in_string = False
    i = 0

    while i < len(values_section):
        char = values_section[i]
        if in_string:
            if char == "'":
                if i + 1 < len(values_section) and values_section[i + 1] == "'":
                    i += 1
                else:
                    in_string = False
        else:
            if char == "'":
                in_string = True
            elif char == "(":
                if depth == 0:
                    start = i + 1
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0 and start is not None:
                    groups.append(values_section[start:i])
                    start = None
        i += 1

    return groups


def parse_sql_values(group: str) -> List[object]:
    values: List[object] = []
    token = []
    in_string = False
    i = 0

    while i < len(group):
        char = group[i]
        if in_string:
            if char == "'":
                if i + 1 < len(group) and group[i + 1] == "'":
                    token.append("'")
                    i += 1
                else:
                    in_string = False
            else:
                token.append(char)
        else:
            if char == "'":
                in_string = True
            elif char == ",":
                values.append(normalize_token("".join(token).strip()))
                token = []
            else:
                token.append(char)
        i += 1

    if token:
        values.append(normalize_token("".join(token).strip()))

    return values


def normalize_token(token: str) -> object:
    if not token or token.upper() == "NULL":
        return None
    if token.startswith("X'") or token.startswith("x'"):
        return None
    if re.fullmatch(r"[-+]?\d+", token):
        return int(token)
    return token


def safe_str(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def to_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if not text:
        return None
    if re.fullmatch(r"[-+]?\d+", text):
        return int(text)
    return None


def parse_date_safe(value: object):
    if not value:
        return None
    if isinstance(value, str):
        if " " in value:
            value = value.split(" ")[0]
    return parse_date(str(value))


def parse_datetime_safe(value: object):
    if not value:
        return None
    dt = parse_datetime(str(value))
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt
