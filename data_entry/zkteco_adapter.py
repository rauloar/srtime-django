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

import logging
from typing import Any, Dict, List, Optional

from zk import ZK


logger = logging.getLogger(__name__)


class ZKTecoAdapterError(Exception):
    """Base exception for ZKTeco adapter failures."""


class ZKTecoConnectionError(ZKTecoAdapterError):
    """Raised when device connection cannot be established."""


class ZKTecoSessionError(ZKTecoAdapterError):
    """Raised when a batch session cannot complete safely."""


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

    @property
    def is_connected(self) -> bool:
        return self._conn is not None

    def connect(self) -> None:
        """Connect to the device. Raises explicit error on failure."""
        if self._conn:
            return
        try:
            self._conn = self._zk.connect()
        except Exception as exc:
            raise ZKTecoConnectionError(
                f"ZKTeco connection failed for {self.ip}:{self.port}: {exc}"
            ) from exc

    def fetch_attendance_batch(self) -> List[Dict[str, Any]]:
        """
        Execute complete batch flow and return normalized raw dicts.

        Flow:
            connect -> disable -> download -> enable -> disconnect
        """
        self.connect()
        try:
            return self.download_attendance()
        finally:
            self.disconnect()

    def fetch_users_batch(self) -> List[Any]:
        """
        Execute complete batch flow and return raw pyzk user records.

        Flow:
            connect -> disable -> download users -> enable -> disconnect
        """
        self.connect()
        try:
            return self.download_users()
        finally:
            self.disconnect()

    def clear_attendance_batch(self) -> bool:
        """
        Execute complete batch flow and clear only attendance logs on device.

        Flow:
            connect -> disable -> clear attendance -> enable -> disconnect
        """
        self.connect()
        try:
            return self.clear_attendance()
        finally:
            self.disconnect()

    def clear_all_data_batch(self) -> bool:
        """
        Execute complete batch flow and clear all device data.

        Flow:
            connect -> disable -> clear all -> enable -> disconnect
        """
        self.connect()
        try:
            return self.clear_all_data()
        finally:
            self.disconnect()

    def sync_users_batch(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute complete batch flow and sync users to device.

        Flow:
            connect -> disable -> set users -> enable -> disconnect
        """
        self.connect()
        try:
            return self.sync_users(users)
        finally:
            self.disconnect()

    def download_attendance(self) -> List[Dict[str, Any]]:
        """
        Download all attendance logs as raw dicts.

        Requires an open connection. Returns empty list if no data.
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        logs = self._run_disabled("attendance", lambda: self._conn.get_attendance() or [])

        return [self._to_raw_dict(log, self.device_id) for log in logs]

    def download_users(self) -> List[Any]:
        """
        Download users from device in a safe disabled session.

        Requires an open connection. Returns empty list if no users exist.
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        users = self._run_disabled("users", lambda: self._conn.get_users() or [])
        return list(users)

    def clear_attendance(self) -> bool:
        """
        Clear attendance logs from device in a safe disabled session.

        Requires an open connection.
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        self._run_disabled("clear attendance", lambda: self._conn.clear_attendance())
        return True

    def clear_all_data(self) -> bool:
        """
        Clear all users/templates/logs from device in a safe disabled session.

        Requires an open connection.
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        self._run_disabled("clear all data", lambda: self._conn.clear_data())
        return True

    def sync_users(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sync users to device in a safe disabled session.

        Input format per user:
            {
                "uid": int,
                "name": str,
                "privilege": int,
                "password": str,
                "group_id": str,
                "user_id": str,
                "card": int,
            }
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        def _apply_sync() -> List[Dict[str, Any]]:
            results: List[Dict[str, Any]] = []
            for user in users:
                user_id = str(user.get("user_id") or "")
                try:
                    self._conn.set_user(
                        uid=int(user.get("uid") or 0),
                        name=str(user.get("name") or ""),
                        privilege=int(user.get("privilege") or 0),
                        password=str(user.get("password") or ""),
                        group_id=str(user.get("group_id") or "0"),
                        user_id=user_id,
                        card=int(user.get("card") or 0),
                    )
                    results.append({"user_id": user_id, "success": True, "error": None})
                except Exception as exc:
                    results.append({"user_id": user_id, "success": False, "error": str(exc)})
            return results

        return self._run_disabled("sync users", _apply_sync)

    def disconnect(self) -> None:
        """Disconnect from the device. Raises explicit error on failure."""
        if not self._conn:
            return
        try:
            self._conn.disconnect()
        except Exception as exc:
            raise ZKTecoSessionError(
                f"ZKTeco disconnect failed for {self.ip}:{self.port}: {exc}"
            ) from exc
        finally:
            self._conn = None

    @staticmethod
    def _to_raw_dict(log: Any, device_id: Optional[str]) -> Dict[str, Any]:
        """Convert a pyzk Attendance record to a simple raw dict."""
        status = getattr(log, "status", 0)
        punch = getattr(log, "punch", 0)

        return {
            "user_id": getattr(log, "user_id", None),
            "timestamp": getattr(log, "timestamp", None),
            "status": int(status) if status is not None else 0,
            "punch": int(punch) if punch is not None else 0,
            "device_id": device_id,
            "source": "zkteco",
            "raw": log,
        }

    def _run_disabled(self, action_name: str, fn):
        """Run a device action while terminal is disabled and always re-enable."""
        action_error: Optional[Exception] = None
        result = None

        try:
            self._conn.disable_device()
            result = fn()
        except Exception as exc:
            action_error = exc
        finally:
            try:
                self._conn.enable_device()
            except Exception as enable_exc:
                if action_error is not None:
                    raise ZKTecoSessionError(
                        f"{action_name} download failed: {action_error}; also failed to re-enable device: {enable_exc}"
                    ) from enable_exc
                raise ZKTecoSessionError(
                    f"Failed to re-enable device after {action_name} download: {enable_exc}"
                ) from enable_exc

        if action_error is not None:
            raise ZKTecoSessionError(f"ZKTeco {action_name} download failed: {action_error}") from action_error

        return result


def build_zkteco_adapter_for_device(device: Any, timeout: int = 10) -> ZKTecoAdapter:
    """Factory helper to instantiate adapter from a Device model instance."""
    return ZKTecoAdapter(
        ip=device.ip,
        port=device.port,
        timeout=timeout,
        device_id=str(getattr(device, "id", "")),
    )
