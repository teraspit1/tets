from __future__ import annotations

import numpy as np

from ecs.components import RigidBody, Transform


class CharacterController:
    def __init__(self, move_speed: float = 4.0, jump_force: float = 5.0) -> None:
        self.move_speed = move_speed
        self.jump_force = jump_force

    def update(self, world, entity: int, input_manager, dt: float) -> None:
        transform = world.get_component(entity, Transform)
        body = world.get_component(entity, RigidBody)
        if transform is None or body is None:
            return

        move = np.zeros(3, dtype=np.float32)
        if input_manager.is_pressed("move_forward"):
            move[2] -= 1
        if input_manager.is_pressed("move_back"):
            move[2] += 1
        if input_manager.is_pressed("move_left"):
            move[0] -= 1
        if input_manager.is_pressed("move_right"):
            move[0] += 1

        if np.linalg.norm(move) > 0:
            move = move / np.linalg.norm(move)
        transform.position += move * self.move_speed * dt

        if input_manager.is_pressed("jump"):
            body.velocity[1] = self.jump_force
