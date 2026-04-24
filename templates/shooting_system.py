from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Projectile:
    owner: int
    speed: float
    ttl: float


class ShootingSystem:
    def __init__(self) -> None:
        self.projectiles: list[Projectile] = []

    def fire(self, owner_entity: int, speed: float = 20.0) -> None:
        self.projectiles.append(Projectile(owner=owner_entity, speed=speed, ttl=2.0))

    def update(self, dt: float) -> None:
        for projectile in self.projectiles:
            projectile.ttl -= dt
        self.projectiles = [p for p in self.projectiles if p.ttl > 0]
