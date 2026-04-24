from __future__ import annotations

import time
from collections import deque


class DebugOverlay:
    def __init__(self, sample_size: int = 120) -> None:
        self.frame_times = deque(maxlen=sample_size)
        self._last = time.perf_counter()

    def tick(self) -> None:
        now = time.perf_counter()
        dt = now - self._last
        self._last = now
        self.frame_times.append(dt)

    @property
    def fps(self) -> float:
        if not self.frame_times:
            return 0.0
        avg = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg if avg > 0 else 0.0

    def as_text(self) -> str:
        return f"FPS: {self.fps:.2f} | Frame Samples: {len(self.frame_times)}"
