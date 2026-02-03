"""
File adapter for attendance data ingestion.

Supports CSV and TXT/LOG formats.

⚠️ IMPORTANT: Format type must be specified explicitly at initialization.
No auto-detection is performed (auto-detection leads to data corruption).

Output: Raw dicts without interpretation or validation.

Supported formats:
- CSV: user_id,timestamp,status,punch (no headers)
- TXT/LOG: user_id : timestamp (status, punch)

Punch values (type of event):
  0 = Entrada
  1 = Salida
  2 = Salida Intermedia
  3 = Entrada Intermedia
  4 = Ext_Ent
  5 = Ext_Sal

Status (capture/verification method):
  0 = Face ID
  1 = Fingerprint
  2 = Password
  3 = RFID Card
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv


class FileAttendanceAdapter:
    """
    Batch adapter for attendance file ingestion.

    Format type MUST be specified explicitly (no auto-detection).
    """

    SUPPORTED_FORMATS = {"csv", "txt", "log"}

    def __init__(
        self,
        file_path: str,
        format_type: str,
        source_device_id: Optional[str] = None,
    ) -> None:
        """
        Initialize adapter.

        Args:
            file_path: Path to the attendance file
            format_type: Explicit format ('csv', 'txt', 'log'). REQUIRED - no auto-detection.
            source_device_id: Optional device identifier for all events

        Raises:
            ValueError: If format_type is not supported
            FileNotFoundError: If file does not exist
        """
        self.file_path = Path(file_path)
        self.format_type = format_type.lower()
        self.source_device_id = source_device_id

        if self.format_type not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {format_type}. Supported: {self.SUPPORTED_FORMATS}"
            )

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

    def read_attendance(self) -> List[Dict[str, Any]]:
        """
        Read attendance file and return raw events.

        Returns:
            List of raw event dicts (user_id, timestamp, status, punch, device_id, raw)

        Raises:
            RuntimeError: If file parsing fails
        """
        try:
            if self.format_type == "csv":
                return self._read_csv()
            else:  # txt or log
                return self._read_txt()
        except Exception as exc:
            raise RuntimeError(
                f"Failed to parse {self.format_type.upper()} file {self.file_path}: {exc}"
            ) from exc

    def _read_csv(self) -> List[Dict[str, Any]]:
        """
        Read CSV format (no headers).

        Format: user_id,timestamp,status,punch

        Status: 0=Face, 1=Fingerprint, 2=Password, 3=RFID
        Punch: 0=Entrada, 1=Salida, 2=Salida_Int, 3=Entrada_Int, 4=Ext_Ent, 5=Ext_Sal
        """
        events = []

        with open(self.file_path, "r") as f:
            reader = csv.reader(f)
            for line_no, row in enumerate(reader, start=1):
                if not row or len(row) < 4:
                    continue  # Skip empty or malformed lines

                try:
                    user_id = row[0].strip()
                    timestamp_str = row[1].strip()
                    status = int(row[2].strip())
                    punch = int(row[3].strip())

                    timestamp = self._parse_timestamp(timestamp_str)

                    events.append({
                        "user_id": user_id,
                        "timestamp": timestamp,
                        "status": status,
                        "punch": punch,
                        "device_id": self.source_device_id,
                        "source": "file",
                        "raw": ",".join(row),
                    })
                except (ValueError, IndexError) as exc:
                    # Skip malformed lines but don't fail
                    continue

        return events

    def _read_txt(self) -> List[Dict[str, Any]]:
        """
        Read TXT/LOG format.

        Format: user_id : timestamp (status, punch)
        Example: 99999 : 2026-02-03 17:07:07 (0, 0)

        Status: 0=Face, 1=Fingerprint, 2=Password, 3=RFID
        Punch: 0=Entrada, 1=Salida, 2=Salida_Int, 3=Entrada_Int, 4=Ext_Ent, 5=Ext_Sal
        """
        events = []

        with open(self.file_path, "r") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    # Parse: "user_id : timestamp (status, punch)"
                    if ":" not in line or "(" not in line or ")" not in line:
                        continue

                    parts = line.split(":")
                    user_id = parts[0].strip()

                    rest = ":".join(parts[1:])  # In case timestamp has ":"
                    ts_part, punch_part = rest.split("(", 1)
                    timestamp_str = ts_part.strip()

                    punch_str = punch_part.rstrip(")")
                    status, punch = [int(x.strip()) for x in punch_str.split(",")]

                    timestamp = self._parse_timestamp(timestamp_str)

                    events.append({
                        "user_id": user_id,
                        "timestamp": timestamp,
                        "status": status,
                        "punch": punch,
                        "device_id": self.source_device_id,
                        "source": "file",
                        "raw": line,
                    })
                except (ValueError, IndexError) as exc:
                    # Skip malformed lines
                    continue

        return events

    @staticmethod
    def _parse_timestamp(timestamp_str: str) -> datetime:
        """
        Parse timestamp string to datetime.

        Accepts:
        - ISO 8601: "2026-02-03T17:07:07"
        - Standard: "2026-02-03 17:07:07"
        """
        # Try ISO format first
        try:
            return datetime.fromisoformat(timestamp_str)
        except ValueError:
            pass

        # Try standard format
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass

        # Fallback: raise
        raise ValueError(f"Cannot parse timestamp: {timestamp_str}")
