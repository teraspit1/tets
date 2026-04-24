from __future__ import annotations

import numpy as np

from ecs.components import AABBCollider, RigidBody, Transform
from ecs.ecs_world import ECSWorld


class PhysicsWorld:
    def __init__(self, world: ECSWorld, gravity: float = -9.81) -> None:
        self.world = world
        self.gravity = gravity

    def step(self, dt: float) -> None:
        for _, (transform, body) in self.world.query(Transform, RigidBody):
            if body.use_gravity:
                body.velocity[1] += self.gravity * dt
            transform.position += body.velocity * dt

        colliders = self.world.query(Transform, AABBCollider)
        for i, (ea, (ta, ca)) in enumerate(colliders):
            for eb, (tb, cb) in colliders[i + 1 :]:
                if self._aabb_overlap(ta.position, ca.half_extents, tb.position, cb.half_extents):
                    self._resolve_overlap(ea, eb)

    @staticmethod
    def _aabb_overlap(pa: np.ndarray, ha: np.ndarray, pb: np.ndarray, hb: np.ndarray) -> bool:
        delta = np.abs(pa - pb)
        return bool(np.all(delta <= (ha + hb)))

    def _resolve_overlap(self, entity_a: int, entity_b: int) -> None:
        body_a = self.world.get_component(entity_a, RigidBody)
        body_b = self.world.get_component(entity_b, RigidBody)
        if body_a is not None:
            body_a.velocity *= 0.0
        if body_b is not None:
            body_b.velocity *= 0.0
