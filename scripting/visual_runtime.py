from __future__ import annotations

import numpy as np

from ecs.components import Transform
from ecs.ecs_world import ECSWorld
from scripting.graph import VisualScriptGraph
from scripting.nodes import UpdateEventNode


class VisualScriptRuntime:
    def __init__(self, world: ECSWorld) -> None:
        self.world = world
        self.graphs: dict[int, VisualScriptGraph] = {}
        self.frame = 0

    def attach_graph(self, entity: int, graph: VisualScriptGraph) -> None:
        self.graphs[entity] = graph

    def update(self, dt: float) -> None:
        for entity, graph in self.graphs.items():
            self._execute_graph(entity, graph, dt)
        self.frame += 1

    def _execute_graph(self, entity: int, graph: VisualScriptGraph, dt: float) -> None:
        for node in graph.nodes.values():
            if isinstance(node, UpdateEventNode) and node.execute({"frame": self.frame}):
                for link in graph.outgoing(node.node_id, "flow"):
                    dst = graph.nodes[link.dst_node]
                    context = {
                        "world": self.world,
                        "entity": entity,
                        "delta": np.array([0.0, 0.0, dt], dtype=np.float32),
                        "TransformType": Transform,
                    }
                    dst.execute(context)
