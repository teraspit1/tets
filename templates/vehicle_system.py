from __future__ import annotations

import numpy as np

from ecs.components import Transform


class VehicleSystem:
    def __init__(self, accel: float = 8.0, turn_speed: float = 120.0) -> None:
        self.accel = accel
        self.turn_speed = turn_speed
        self.speed_by_entity: dict[int, float] = {}

    def update(self, world, entity: int, throttle: float, steering: float, dt: float) -> None:
        transform = world.get_component(entity, Transform)
        if transform is None:
            return
        speed = self.speed_by_entity.get(entity, 0.0)
        speed += throttle * self.accel * dt
        self.speed_by_entity[entity] = speed * 0.98

        transform.rotation[1] += steering * self.turn_speed * dt
        forward = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        transform.position += forward * self.speed_by_entity[entity] * dt
