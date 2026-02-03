"""
ZKTeco batch adapter (pyzk).

Flow enforced (batch-only):
    connect -> disable terminal -> download attendance -> enable terminal -> disconnect

Design rules:
- No persistence
- No business logic
- No IN/OUT interpretation
- No live_capture usage
"""

from typing import Any, Dict, List, Optional

from zk import ZK


class ZKTecoAdapter:
    """
    Batch-only adapter for ZKTeco devices using pyzk.

    This adapter only retrieves raw attendance logs and returns
    simple data structures (dicts) without interpretation.
    """

    def __init__(
        self,
        ip: str,
        port: int = 4370,
        timeout: int = 5,
        password: int = 0,
        force_udp: bool = False,
        ommit_ping: bool = False,
        device_id: Optional[str] = None,
    ) -> None:
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.password = password
        self.force_udp = force_udp
        self.ommit_ping = ommit_ping
        self.device_id = device_id

        self._zk = ZK(
            ip,
            port=port,
            timeout=timeout,
            password=password,
            force_udp=force_udp,
            ommit_ping=ommit_ping,
        )
        self._conn = None

    def connect(self) -> None:
        """Connect to the device. Raises explicit error on failure."""
        if self._conn:
            return
        try:
            self._conn = self._zk.connect()
        except Exception as exc:
            raise ConnectionError(
                f"ZKTeco connection failed for {self.ip}:{self.port}: {exc}"
            ) from exc

    def download_attendance(self) -> List[Dict[str, Any]]:
        """
        Download all attendance logs as raw dicts.

        Requires an open connection. Returns empty list if no data.
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        download_error: Optional[Exception] = None
        logs: List[Any] = []

        try:
            self._conn.disable_device()
            logs = self._conn.get_attendance() or []
        except Exception as exc:
            download_error = exc
        finally:
            try:
                self._conn.enable_device()
            except Exception as enable_exc:
                if download_error is not None:
                    raise RuntimeError(
                        f"Download failed: {download_error}; also failed to re-enable device: {enable_exc}"
                    ) from enable_exc
                raise RuntimeError(
                    f"Failed to re-enable device after download: {enable_exc}"
                ) from enable_exc

        if download_error is not None:
            raise RuntimeError(f"ZKTeco download failed: {download_error}") from download_error

        return [self._to_raw_dict(log, self.device_id) for log in logs]

    def disconnect(self) -> None:
        """Disconnect from the device. Raises explicit error on failure."""
        if not self._conn:
            return
        try:
            self._conn.disconnect()
        except Exception as exc:
            raise RuntimeError(
                f"ZKTeco disconnect failed for {self.ip}:{self.port}: {exc}"
            ) from exc
        finally:
            self._conn = None

    @staticmethod
    def _to_raw_dict(log: Any, device_id: Optional[str]) -> Dict[str, Any]:
        """Convert a pyzk Attendance record to a simple raw dict."""
        return {
            "user_id": getattr(log, "user_id", None),
            "timestamp": getattr(log, "timestamp", None),
            "device_id": device_id,
            "raw": log,
        }
