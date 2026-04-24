from __future__ import annotations

from dataclasses import dataclass

from scripting.nodes import Node


@dataclass
class Link:
    src_node: str
    src_pin: str
    dst_node: str
    dst_pin: str


class VisualScriptGraph:
    def __init__(self, name: str) -> None:
        self.name = name
        self.nodes: dict[str, Node] = {}
        self.links: list[Link] = []

    def add_node(self, node: Node) -> None:
        self.nodes[node.node_id] = node

    def add_link(self, src_node: str, src_pin: str, dst_node: str, dst_pin: str) -> None:
        self.links.append(Link(src_node, src_pin, dst_node, dst_pin))

    def outgoing(self, node_id: str, pin: str | None = None) -> list[Link]:
        links = [link for link in self.links if link.src_node == node_id]
        if pin is not None:
            links = [link for link in links if link.src_pin == pin]
        return links
