from __future__ import annotations

import time


class Time:
    def __init__(self) -> None:
        self._last = time.perf_counter()
        self.delta_time = 0.0
        self.total_time = 0.0

    def update(self) -> None:
        now = time.perf_counter()
        self.delta_time = now - self._last
        self._last = now
        self.total_time += self.delta_time
