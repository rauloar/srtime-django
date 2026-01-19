"""
ZK Device Service - Wrapper para pyzk library
"""
from zk import ZK, const
from typing import List, Dict, Any, Optional

class ZKService:
    def __init__(self, ip: str, port: int = 4370, timeout: int = 5, password: int = 0, force_udp: bool = False, ommit_ping: bool = False):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.password = password
        self.force_udp = force_udp
        self.ommit_ping = ommit_ping
        self.zk = ZK(ip, port=port, timeout=timeout, password=password, force_udp=force_udp, ommit_ping=ommit_ping)
        self.conn = None

    def connect(self):
        self.conn = self.zk.connect()
        return self.conn

    def disconnect(self):
        if self.conn:
            self.conn.disconnect()

    def test_connection(self) -> Dict[str, Any]:
        try:
            self.connect()
            firmware = self.conn.get_firmware_version()
            serial = self.conn.get_serialnumber()
            platform = self.conn.get_platform()
            return {
                "success": True, 
                "message": "Connection successful", 
                "firmware_version": firmware, 
                "serial_number": serial, 
                "platform": platform
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            self.disconnect()

    def get_users(self) -> List[Any]:
        try:
            self.connect()
            users = self.conn.get_users()
            return users
        except Exception as e:
            raise e
        finally:
            self.disconnect()

    def get_attendance(self) -> List[Any]:
        try:
            self.connect()
            logs = self.conn.get_attendance()
            return logs
        except Exception as e:
            raise e
        finally:
            self.disconnect()

    def set_user(self, uid: int, name: str, privilege: int, password: str, group_id: str, user_id: str, card: int) -> bool:
        try:
            self.connect()
            self.conn.set_user(uid=uid, name=name, privilege=privilege, password=password, group_id=group_id, user_id=user_id, card=card)
            return True
        except Exception as e:
            raise e
        finally:
            self.disconnect()

    def delete_user(self, user_id: str) -> bool:
        try:
            self.connect()
            self.conn.delete_user(user_id=user_id)
            return True
        except Exception as e:
            raise e
        finally:
            self.disconnect()
            
    def clear_attendance(self) -> bool:
        try:
            self.connect()
            self.conn.clear_attendance()
            return True
        except Exception as e:
            raise e
        finally:
            self.disconnect()
            
    def enable_device(self) -> bool:
        try:
            self.connect()
            self.conn.enable_device()
            return True
        except Exception as e:
            raise e
        finally:
            self.disconnect()

    def disable_device(self) -> bool:
        try:
            self.connect()
            self.conn.disable_device()
            return True
        except Exception as e:
            raise e
        finally:
            self.disconnect()

    def get_info(self) -> Dict[str, Any]:
        try:
            self.connect()
            firmware = self.conn.get_firmware_version()
            serial = self.conn.get_serialnumber()
            platform = self.conn.get_platform()
            mac = self.conn.get_mac()
            device_name = self.conn.get_device_name()
            
            # Extend with counts
            self.conn.read_sizes()
            users_count = self.conn.users
            fingers_count = self.conn.fingers
            records_count = self.conn.records
            faces_count = getattr(self.conn, 'faces', 0)
            
            return {
                "success": True,
                "firmware_version": firmware,
                "serial_number": serial,
                "platform": platform,
                "mac": mac,
                "device_name": device_name,
                "users_count": users_count,
                "fingers_count": fingers_count,
                "records_count": records_count,
                "faces_count": faces_count
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            self.disconnect()

    def restart_device(self) -> Dict[str, Any]:
        try:
            self.connect()
            self.conn.restart()
            return {"success": True, "message": "Device restarted"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            self.disconnect()

    def poweroff_device(self) -> Dict[str, Any]:
        try:
            self.connect()
            self.conn.poweroff()
            return {"success": True, "message": "Device powered off"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            self.disconnect()

    def sync_time(self) -> Dict[str, Any]:
        try:
            self.connect()
            from datetime import datetime
            self.conn.set_time(datetime.now())
            return {"success": True, "message": "Time synced"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            self.disconnect()

    def test_voice(self, voice_index: int = 0) -> Dict[str, Any]:
        try:
            self.connect()
            self.conn.test_voice(index=voice_index)
            return {"success": True, "message": f"Voice {voice_index} tested"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            self.disconnect()

    def get_memory_info(self) -> Dict[str, Any]:
        try:
            self.connect()
            self.conn.read_sizes()
            return {
                "success": True,
                "users": self.conn.users,
                "fingers": self.conn.fingers,
                "records": self.conn.records,
                "faces": getattr(self.conn, 'faces', 0),
                "users_cap": getattr(self.conn, 'users_cap', 0),
                "fingers_cap": getattr(self.conn, 'fingers_cap', 0)
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            self.disconnect()

    def clear_all_data(self) -> Dict[str, Any]:
        try:
            self.connect()
            self.conn.clear_data()
            return {"success": True, "message": "All data cleared"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            self.disconnect()

    def get_recent_attendance(self, limit: int = 50) -> Dict[str, Any]:
        try:
            self.connect()
            logs = self.conn.get_attendance()
            # Return most recent
            recent_logs = list(logs)[-limit:] if logs else []
            
            result = []
            for log in recent_logs:
                result.append({
                    "user_id": log.user_id,
                    "timestamp": log.timestamp.isoformat() if hasattr(log.timestamp, 'isoformat') else str(log.timestamp),
                    "status": log.status,
                    "punch": log.punch
                })
            
            return {"success": True, "logs": result, "count": len(result)}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            self.disconnect()

    def get_templates(self) -> List[Any]:
        try:
            self.connect()
            templates = self.conn.get_templates()
            return templates
        except Exception as e:
            raise e
        finally:
            self.disconnect()

# Helper to instantiate service
def get_zk_service(ip: str, port: int = 4370, timeout: int = 15):
    return ZKService(ip, port, timeout=timeout, ommit_ping=True)
