from __future__ import annotations


class TimeOfDaySystem:
    def __init__(self, day_length_seconds: float = 300.0) -> None:
        self.day_length_seconds = day_length_seconds
        self.clock = 0.0

    def update(self, dt: float) -> None:
        self.clock = (self.clock + dt) % self.day_length_seconds

    @property
    def normalized(self) -> float:
        return self.clock / self.day_length_seconds
