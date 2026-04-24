from __future__ import annotations

import numpy as np


def perspective(fov_deg: float, aspect: float, near: float, far: float) -> np.ndarray:
    f = 1.0 / np.tan(np.deg2rad(fov_deg) / 2.0)
    mat = np.zeros((4, 4), dtype=np.float32)
    mat[0, 0] = f / aspect
    mat[1, 1] = f
    mat[2, 2] = (far + near) / (near - far)
    mat[2, 3] = (2 * far * near) / (near - far)
    mat[3, 2] = -1.0
    return mat


def view_matrix(position: np.ndarray) -> np.ndarray:
    mat = np.eye(4, dtype=np.float32)
    mat[0:3, 3] = -position[0:3]
    return mat
