from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from ecs.components import AABBCollider, Camera, MeshRenderer, RigidBody, Transform
from ecs.ecs_world import ECSWorld
from ecs.scene import Scene, SceneNode


def _normalize(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value


class SceneSerializer:
    COMPONENT_TYPES = {
        "Transform": Transform,
        "MeshRenderer": MeshRenderer,
        "Camera": Camera,
        "RigidBody": RigidBody,
        "AABBCollider": AABBCollider,
    }

    def save(self, scene: Scene, path: str) -> None:
        data = {
            "scene": scene.name,
            "nodes": {
                str(entity): {
                    "name": node.name,
                    "parent": node.parent,
                    "children": node.children,
                }
                for entity, node in scene.nodes.items()
            },
            "world": _normalize(scene.world.to_dict()),
        }
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load_into(self, scene: Scene, path: str) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        world: ECSWorld = scene.world

        # reset scene/world
        for entity in list(world.entities):
            world.destroy_entity(entity)
        scene.nodes.clear()

        # recreate entities with original ids to keep references stable
        entities = [int(eid) for eid in data.get("world", {}).get("entities", [])]
        if entities:
            world._next_entity_id = max(entities) + 1
        for entity in entities:
            world.entities.add(entity)

        for entity_str, node_data in data.get("nodes", {}).items():
            entity = int(entity_str)
            scene.nodes[entity] = SceneNode(
                entity=entity,
                name=node_data["name"],
                parent=node_data["parent"],
                children=node_data["children"],
            )

        for comp_name, comp_entries in data.get("world", {}).get("components", {}).items():
            ctype = self.COMPONENT_TYPES.get(comp_name)
            if ctype is None:
                continue
            for entity_str, payload in comp_entries.items():
                entity = int(entity_str)
                world.add_component(entity, self._deserialize_component(ctype, payload))

    def _deserialize_component(self, ctype: type, payload: dict[str, Any]) -> Any:
        parsed = {}
        for key, value in payload.items():
            if isinstance(value, list):
                parsed[key] = np.array(value, dtype=np.float32)
            else:
                parsed[key] = value
        return ctype(**parsed)

    def load_stub(self, path: str) -> tuple[str, dict[str, Any]]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data["scene"], data
