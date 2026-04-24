from __future__ import annotations

from dataclasses import dataclass, field

from ecs.ecs_world import ECSWorld


@dataclass
class SceneNode:
    entity: int
    name: str
    parent: int | None = None
    children: list[int] = field(default_factory=list)


class Scene:
    def __init__(self, name: str, world: ECSWorld) -> None:
        self.name = name
        self.world = world
        self.nodes: dict[int, SceneNode] = {}

    def create_node(self, name: str, parent: int | None = None) -> int:
        entity = self.world.create_entity()
        self.nodes[entity] = SceneNode(entity=entity, name=name, parent=parent)
        if parent is not None and parent in self.nodes:
            self.nodes[parent].children.append(entity)
        return entity

    def remove_node(self, entity: int) -> None:
        node = self.nodes.get(entity)
        if not node:
            return
        if node.parent is not None and node.parent in self.nodes:
            self.nodes[node.parent].children.remove(entity)
        for child in list(node.children):
            self.remove_node(child)
        self.world.destroy_entity(entity)
        del self.nodes[entity]
