from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InputAction:
    name: str
    key: str


class InputManager:
    def __init__(self) -> None:
        self.bindings: dict[str, InputAction] = {
            "move_forward": InputAction("move_forward", "W"),
            "move_back": InputAction("move_back", "S"),
            "move_left": InputAction("move_left", "A"),
            "move_right": InputAction("move_right", "D"),
            "jump": InputAction("jump", "SPACE"),
            "shoot": InputAction("shoot", "MOUSE1"),
        }
        self.state: dict[str, bool] = {name: False for name in self.bindings}

    def bind(self, action_name: str, key: str) -> None:
        self.bindings[action_name] = InputAction(action_name, key)
        self.state.setdefault(action_name, False)

    def poll(self) -> None:
        # Input polling bridge for glfw/OS hooks would be implemented here.
        pass

    def is_pressed(self, action_name: str) -> bool:
        return self.state.get(action_name, False)
