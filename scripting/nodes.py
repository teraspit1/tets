from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Pin:
    name: str


@dataclass
class Node:
    node_id: str
    title: str
    inputs: list[Pin] = field(default_factory=list)
    outputs: list[Pin] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    def execute(self, context: dict[str, Any]) -> Any:
        raise NotImplementedError


class StartEventNode(Node):
    def __init__(self, node_id: str) -> None:
        super().__init__(node_id=node_id, title="Start", outputs=[Pin("flow")])

    def execute(self, context: dict[str, Any]) -> bool:
        return context.get("frame", 0) == 0


class UpdateEventNode(Node):
    def __init__(self, node_id: str) -> None:
        super().__init__(node_id=node_id, title="Update", outputs=[Pin("flow")])

    def execute(self, context: dict[str, Any]) -> bool:
        return True


class BranchNode(Node):
    def __init__(self, node_id: str) -> None:
        super().__init__(
            node_id=node_id,
            title="Branch",
            inputs=[Pin("condition")],
            outputs=[Pin("true"), Pin("false")],
        )

    def execute(self, context: dict[str, Any]) -> str:
        return "true" if bool(context.get("condition", False)) else "false"


class AddNode(Node):
    def __init__(self, node_id: str) -> None:
        super().__init__(node_id=node_id, title="Add", inputs=[Pin("a"), Pin("b")], outputs=[Pin("sum")])

    def execute(self, context: dict[str, Any]) -> float:
        return float(context.get("a", 0.0)) + float(context.get("b", 0.0))


class TransformTranslateNode(Node):
    def __init__(self, node_id: str) -> None:
        super().__init__(
            node_id=node_id,
            title="Translate",
            inputs=[Pin("entity"), Pin("delta")],
            outputs=[Pin("flow")],
        )

    def execute(self, context: dict[str, Any]) -> bool:
        world = context["world"]
        transform = world.get_component(context["entity"], context["TransformType"])
        if transform is None:
            return False
        transform.position += context.get("delta")
        return True
