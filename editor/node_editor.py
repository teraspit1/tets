from __future__ import annotations

from scripting.graph import VisualScriptGraph


class NodeEditor:
    def __init__(self) -> None:
        self.selected_node: str | None = None

    def connect(self, graph: VisualScriptGraph, src_node: str, src_pin: str, dst_node: str, dst_pin: str) -> None:
        graph.add_link(src_node, src_pin, dst_node, dst_pin)

    def list_nodes(self, graph: VisualScriptGraph) -> list[str]:
        return [f"{node.node_id}:{node.title}" for node in graph.nodes.values()]
