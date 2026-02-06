"""
Enumeration definitions for attendance system.
Source of truth for all enum values used across API responses.
"""

# Punch Status (from biometric device)
PUNCH_STATUS = {
    0: {'code': 0, 'label': 'Entrada', 'display': 'Entrada'},
    1: {'code': 1, 'label': 'Salida', 'display': 'Salida'},
    2: {'code': 2, 'label': 'Inicio Descanso', 'display': 'Inicio Descanso'},
    3: {'code': 3, 'label': 'Fin Descanso', 'display': 'Fin Descanso'},
    4: {'code': 4, 'label': 'Inicio Horas Extras', 'display': 'Inicio Horas Extras'},
    5: {'code': 5, 'label': 'Fin Horas Extras', 'display': 'Fin Horas Extras'},
}

# Verify Mode (biometric method)
VERIFY_MODE = {
    1: {'code': 1, 'label': 'Huella', 'display': 'Huella Dactilar'},
    3: {'code': 3, 'label': 'Contraseña', 'display': 'Contraseña'},
    4: {'code': 4, 'label': 'Tarjeta', 'display': 'Tarjeta RFID'},
    15: {'code': 15, 'label': 'Rostro', 'display': 'Reconocimiento Facial'},
    25: {'code': 25, 'label': 'Palma', 'display': 'Reconocimiento de Palma'},
}

# Attendance Status (calculated)
ATTENDANCE_STATUS = {
    'Normal': {
        'code': 'Normal',
        'label': 'Normal',
        'display': 'Presentismo',
        'color': '#2e7d32',  # Green (light mode)
        'color_dark': '#4ade80',  # Green (dark mode)
        'icon': 'check-circle'
    },
    'Absent': {
        'code': 'Absent',
        'label': 'Absent',
        'display': 'Ausente',
        'color': '#c62828',  # Red (light mode)
        'color_dark': '#f87171',  # Red (dark mode)
        'icon': 'x-circle'
    },
    'Late': {
        'code': 'Late',
        'label': 'Late',
        'display': 'Llegó Tarde',
        'color': '#ef6c00',  # Orange (light mode)
        'color_dark': '#fbbf24',  # Orange (dark mode)
        'icon': 'alert-circle'
    },
    'Early': {
        'code': 'Early',
        'label': 'Early',
        'display': 'Salió Temprano',
        'color': '#f9a825',  # Yellow (light mode)
        'color_dark': '#fcd34d',  # Yellow (dark mode)
        'icon': 'clock'
    },
    'Partial': {
        'code': 'Partial',
        'label': 'Partial',
        'display': 'Parcial',
        'color': '#afb42b',  # Lime (light mode)
        'color_dark': '#dcf323',  # Lime (dark mode)
        'icon': 'minus-circle'
    },
    'Leave': {
        'code': 'Leave',
        'label': 'Leave',
        'display': 'Licencia',
        'color': '#7b1fa2',  # Purple (light mode)
        'color_dark': '#d084d0',  # Purple (dark mode)
        'icon': 'calendar'
    },
    'Worked': {
        'code': 'Worked',
        'label': 'Worked',
        'display': 'Trabajado',
        'color': '#0277bd',  # Cyan (light mode)
        'color_dark': '#67d9ff',  # Cyan (dark mode)
        'icon': 'briefcase'
    },
    'Incomplete': {
        'code': 'Incomplete',
        'label': 'Incomplete',
        'display': 'Incompleto',
        'color': '#9e9e9e',  # Gray (light mode)
        'color_dark': '#d3d3d3',  # Gray (dark mode)
        'icon': 'alert'
    },
    'Excessive': {
        'code': 'Excessive',
        'label': 'Excessive',
        'display': 'Excesivo',
        'color': '#b71c1c',  # Dark Red (light mode)
        'color_dark': '#ff6e6e',  # Light Red (dark mode)
        'icon': 'alert-triangle'
    },
    'HolidayWorked': {
        'code': 'HolidayWorked',
        'label': 'HolidayWorked',
        'display': 'Trabajo en Feriado',
        'color': '#e65100',  # Deep Orange (light mode)
        'color_dark': '#ffb74d',  # Light Orange (dark mode)
        'icon': 'gift'
    },
    'Rest Day': {
        'code': 'Rest Day',
        'label': 'Rest Day',
        'display': 'Día de Descanso',
        'color': '#1565c0',  # Blue (light mode)
        'color_dark': '#60a5fa',  # Blue (dark mode)
        'icon': 'sun'
    },
}

# Attendance status groupings (for summaries and reports)
ATTENDANCE_PRESENT_STATUSES = {
    'Normal',
    'Late',
    'Early',
    'Partial',
    'Worked',
    'HolidayWorked'
}

ATTENDANCE_ABSENT_STATUS = 'Absent'


def get_punch_status_label(status_code, default_prefix='Estado'):
    """Get label for punch status code"""
    if status_code in PUNCH_STATUS:
        return PUNCH_STATUS[status_code]['label']
    return f'{default_prefix} {status_code}'


def get_verify_mode_label(verify_mode_code, default_prefix='Modo'):
    """Get label for verify mode code"""
    if verify_mode_code in VERIFY_MODE:
        return VERIFY_MODE[verify_mode_code]['label']
    return f'{default_prefix} {verify_mode_code}'


def get_attendance_status_info(status_code):
    """Get full info (label, display, colors) for attendance status"""
    if status_code in ATTENDANCE_STATUS:
        return ATTENDANCE_STATUS[status_code]
    return {
        'code': status_code,
        'label': status_code,
        'display': status_code,
        'color': '#666666',
        'color_dark': '#999999',
        'icon': 'help-circle'
    }
