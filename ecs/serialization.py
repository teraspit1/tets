from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from ecs.ecs_world import ECSWorld
from ecs.scene import Scene


def _normalize(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value


class SceneSerializer:
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

    def load_stub(self, path: str) -> tuple[str, dict[str, Any]]:
        # For MVP, we expose parsed JSON so project code can map data back into
        # concrete component dataclasses with explicit constructors.
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data["scene"], data
