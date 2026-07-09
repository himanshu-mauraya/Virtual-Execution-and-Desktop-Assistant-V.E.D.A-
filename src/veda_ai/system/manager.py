from __future__ import annotations

import logging
import subprocess

logger = logging.getLogger(__name__)


class SystemManager:
    """Windows system control utilities for VEDA AI."""

    def shutdown(self) -> None:
        logger.info("Shutting down PC")
        subprocess.run(["shutdown", "/s", "/t", "30"], check=False)

    def restart(self) -> None:
        logger.info("Restarting PC")
        subprocess.run(["shutdown", "/r", "/t", "30"], check=False)

    def lock(self) -> None:
        logger.info("Locking PC")
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)

    def sleep(self) -> None:
        logger.info("Putting PC to sleep")
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"], check=False)
