from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MeshResource:
    path: str


@dataclass
class TextureResource:
    path: str


@dataclass
class ShaderResource:
    vertex_path: str
    fragment_path: str


class ResourceManager:
    def __init__(self, root: str = "assets") -> None:
        self.root = Path(root)
        self.meshes: dict[str, MeshResource] = {}
        self.textures: dict[str, TextureResource] = {}
        self.shaders: dict[str, ShaderResource] = {}

    def register_mesh(self, name: str, relative_path: str) -> None:
        self.meshes[name] = MeshResource(str(self.root / relative_path))

    def register_texture(self, name: str, relative_path: str) -> None:
        self.textures[name] = TextureResource(str(self.root / relative_path))

    def register_shader(self, name: str, vert_rel: str, frag_rel: str) -> None:
        self.shaders[name] = ShaderResource(str(self.root / vert_rel), str(self.root / frag_rel))
