"""
Device adapter factory.

Centralizes adapter/service selection for device operations.
- mode='legacy': returns legacy ZK service (full command surface)
- mode='batch': returns professional batch adapter
"""

from typing import Any, Literal

from data_entry.zkteco_adapter import build_zkteco_adapter_for_device
from .zk import get_zk_service

AdapterMode = Literal["legacy", "batch"]


def get_device_adapter(device: Any, timeout: int = 10, mode: AdapterMode = "legacy"):
    """Return the proper adapter/service instance for a device operation."""
    if mode == "batch":
        return build_zkteco_adapter_for_device(device, timeout=timeout)

    return get_zk_service(device.ip, device.port, timeout=timeout)
