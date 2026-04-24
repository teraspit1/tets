from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np


@dataclass
class Transform:
    position: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    rotation: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    scale: np.ndarray = field(default_factory=lambda: np.ones(3, dtype=np.float32))


@dataclass
class MeshRenderer:
    mesh_id: str
    material_id: str
    visible: bool = True


@dataclass
class Camera:
    fov: float = 60.0
    near: float = 0.1
    far: float = 1000.0
    is_main: bool = False


@dataclass
class RigidBody:
    mass: float = 1.0
    use_gravity: bool = True
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))


@dataclass
class AABBCollider:
    half_extents: np.ndarray = field(default_factory=lambda: np.array([0.5, 0.5, 0.5], dtype=np.float32))
    is_trigger: bool = False
