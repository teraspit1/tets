from __future__ import annotations

import json
from pathlib import Path

from scripting.graph import VisualScriptGraph


class GraphSerializer:
    def save(self, graph: VisualScriptGraph, path: str) -> None:
        data = {
            "name": graph.name,
            "nodes": [
                {
                    "id": node.node_id,
                    "title": node.title,
                    "data": node.data,
                    "inputs": [pin.name for pin in node.inputs],
                    "outputs": [pin.name for pin in node.outputs],
                }
                for node in graph.nodes.values()
            ],
            "links": [link.__dict__ for link in graph.links],
        }
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
