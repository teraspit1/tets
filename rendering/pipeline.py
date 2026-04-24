from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PS1PipelineConfig:
    affine_texture_warp: bool = True
    vertex_jitter: float = 0.02
    color_depth_bits: int = 5
    low_res_scale: float = 0.5
    dithering: bool = True


class Pipeline:
    def __init__(self, config: PS1PipelineConfig) -> None:
        self.config = config

    def quantize_color(self, rgb: tuple[float, float, float]) -> tuple[float, float, float]:
        levels = (2**self.config.color_depth_bits) - 1
        return tuple(round(channel * levels) / levels for channel in rgb)
