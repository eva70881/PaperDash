"""Utility functions for collecting system usage statistics."""

from __future__ import annotations

import os
import shutil
import time
from typing import Iterable, Tuple

IGNORED_FS_TYPES = {
    "autofs",
    "bpf",
    "cgroup",
    "cgroup2",
    "configfs",
    "debugfs",
    "devpts",
    "devtmpfs",
    "efivarfs",
    "fusectl",
    "hugetlbfs",
    "mqueue",
    "proc",
    "pstore",
    "ramfs",
    "securityfs",
    "sysfs",
    "tmpfs",
    "tracefs",
}

IGNORED_PATH_PREFIXES = (
    "/proc",
    "/run",
    "/sys",
    "/tmp",
    "/var/lib/docker",
    "/var/run",
    "/dev",
    "/snap",
)


def _read_cpu_times() -> Tuple[int, int]:
    """Return cumulative total and idle CPU jiffies from /proc/stat."""

    with open("/proc/stat", "r", encoding="utf-8") as stat_file:
        for line in stat_file:
            if line.startswith("cpu "):
                parts = line.split()
                values = [int(value) for value in parts[1:]]
                idle = values[3] + values[4]
                total = sum(values)
                return total, idle

    raise RuntimeError("Unable to read CPU statistics from /proc/stat")


def get_cpu_usage_percent(interval: float = 0.2) -> float:
    """Return CPU utilisation percentage over a short interval."""

    total_before, idle_before = _read_cpu_times()
    time.sleep(interval)
    total_after, idle_after = _read_cpu_times()

    delta_total = total_after - total_before
    delta_idle = idle_after - idle_before

    if delta_total <= 0:
        return 0.0

    usage = 100.0 * (1.0 - (delta_idle / delta_total))
    return max(0.0, min(usage, 100.0))


def get_memory_usage_percent() -> float:
    """Return memory utilisation percentage using /proc/meminfo."""

    meminfo: dict[str, int] = {}
    with open("/proc/meminfo", "r", encoding="utf-8") as meminfo_file:
        for line in meminfo_file:
            key, value = line.split(":", 1)
            meminfo[key] = int(value.strip().split()[0])

    total_kb = meminfo.get("MemTotal", 0)
    available_kb = meminfo.get("MemAvailable")

    if total_kb <= 0:
        return 0.0

    if available_kb is None:
        free_kb = meminfo.get("MemFree", 0)
        buffers_kb = meminfo.get("Buffers", 0)
        cached_kb = meminfo.get("Cached", 0)
        available_kb = free_kb + buffers_kb + cached_kb

    used_kb = max(0, total_kb - available_kb)
    usage = 100.0 * used_kb / total_kb
    return max(0.0, min(usage, 100.0))


def _valid_mount_point(path: str, fstype: str) -> bool:
    if fstype in IGNORED_FS_TYPES:
        return False

    for prefix in IGNORED_PATH_PREFIXES:
        if path == prefix or path.startswith(prefix + "/"):
            return False

    return os.path.isdir(path)


def _iter_mount_points() -> Iterable[str]:
    seen: set[str] = set()
    with open("/proc/mounts", "r", encoding="utf-8") as mounts_file:
        for line in mounts_file:
            parts = line.split()
            if len(parts) < 3:
                continue
            _device, mountpoint, fstype = parts[:3]
            if not _valid_mount_point(mountpoint, fstype):
                continue
            if mountpoint in seen:
                continue
            seen.add(mountpoint)
            yield mountpoint


def get_drive_usage_percent() -> float:
    """Return overall disk utilisation percentage across real mount points."""

    total_bytes = 0
    used_bytes = 0

    for mountpoint in _iter_mount_points():
        try:
            usage = shutil.disk_usage(mountpoint)
        except OSError:
            continue

        total_bytes += usage.total
        used_bytes += usage.total - usage.free

    if total_bytes <= 0:
        return 0.0

    usage_percent = 100.0 * used_bytes / total_bytes
    return max(0.0, min(usage_percent, 100.0))


def get_system_usage() -> Tuple[float, float, float]:
    """Return CPU, memory, and drive usage percentages."""

    cpu_percent = get_cpu_usage_percent()
    memory_percent = get_memory_usage_percent()
    drive_percent = get_drive_usage_percent()
    return cpu_percent, memory_percent, drive_percent
