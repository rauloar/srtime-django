# Audit and Usage Manual (Alpha)

This document describes the current attendance workflow and the audit fields added for manual log edits. It is intentionally brief because the system is still in alpha.

## Scope
- Manual edits are done day-by-day by HR.
- After edits, the period can be recalculated to produce a corrected report.
- The system never stops processing; it records reasons for absences and missing schedules.

## Core Endpoints
- Raw attendance logs (CRUD): /api/v1/attendance-logs/
- Raw attendance logs (read alias): /api/v1/attendance/logs/
- Daily attendance (calculated): /api/v1/daily-attendance/
- Calculate period: /api/v1/attendance/calculate/
- Calculate period (detailed): /api/v1/attendance/calculate/detailed/
- Absences (leave records): /api/v1/leaves/
- Absences alias: /api/v1/attendance/absences/
- Holidays: /api/v1/holidays/

## Manual Edit Fields (AttendanceLog)
The raw log supports audit fields for manual corrections:
- edited_reason: why the log was edited
- edited_by: who edited it (auto from authenticated user if present)
- edited_at: when it was edited
- is_manual: true when the log is manual or edited

Example (PATCH):
- edited_reason: "Terminal offline, employee could not punch"
- is_manual: true

## Processing Flow
1) HR edits a specific log day-by-day with a reason.
2) Run calculate period for the date range.
3) Review the daily attendance report.

## Absence Transparency
Daily attendance includes exception_reason for missing schedule or configuration:
- IMPLICIT_REST: no schedule configured
- SHIFT_NO_TIMETABLES: shift assigned but no timetables
- SHIFT_TIMETABLE_MISSING_DAY: no timetable for day of week

These reasons allow HR to review and decide if the absence is justified, a configuration issue, or expected.

## Recommended Queries
- Absences in a period:
  - /api/v1/daily-attendance/?is_absent=true&date__gte=YYYY-MM-DD&date__lte=YYYY-MM-DD
- Filter by reason:
  - /api/v1/daily-attendance/?is_absent=true&search=SHIFT_NO_TIMETABLES
