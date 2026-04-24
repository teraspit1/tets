from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ShaderProgram:
    name: str
    vertex_source: str
    fragment_source: str


class ShaderSystem:
    def __init__(self) -> None:
        self.programs: dict[str, ShaderProgram] = {}

    def load(self, name: str, vertex_path: str, fragment_path: str) -> ShaderProgram:
        vert = Path(vertex_path).read_text(encoding="utf-8")
        frag = Path(fragment_path).read_text(encoding="utf-8")
        program = ShaderProgram(name, vert, frag)
        self.programs[name] = program
        return program
